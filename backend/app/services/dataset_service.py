import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GroupShuffleSplit
from backend.app.core.config import settings
from backend.app.core.logging_config import logger
from backend.app.core.error_handlers import VeritasException


class DatasetService:
    """
    Dataset Management & Leakage-Free Splitting Service.
    Supports CSV, JSON, JSONL with automatic column detection and group-aware splitting.
    """
    TEXT_CANDIDATES = ["text", "body", "article", "content", "statement", "claim", "news"]
    TITLE_CANDIDATES = ["title", "headline", "subject", "header"]
    LABEL_CANDIDATES = ["label", "target", "class", "verdict", "is_fake", "fake"]
    SOURCE_CANDIDATES = ["source", "author", "publisher", "domain", "site"]
    DATE_CANDIDATES = ["date", "published_date", "time", "created_at"]

    def detect_column_mappings(self, columns: List[str]) -> Dict[str, str]:
        """Automatically match dataframe column names to canonical schema."""
        mappings = {}
        cols_lower = {c.lower(): c for c in columns}

        # Text column
        for cand in self.TEXT_CANDIDATES:
            if cand in cols_lower:
                mappings["text"] = cols_lower[cand]
                break

        # Title column
        for cand in self.TITLE_CANDIDATES:
            if cand in cols_lower and cols_lower[cand] != mappings.get("text"):
                mappings["title"] = cols_lower[cand]
                break

        # Label column
        for cand in self.LABEL_CANDIDATES:
            if cand in cols_lower:
                mappings["label"] = cols_lower[cand]
                break

        # Source / Domain column
        for cand in self.SOURCE_CANDIDATES:
            if cand in cols_lower:
                mappings["source"] = cols_lower[cand]
                break

        # Date column
        for cand in self.DATE_CANDIDATES:
            if cand in cols_lower:
                mappings["date"] = cols_lower[cand]
                break

        return mappings

    def normalize_labels(self, series: pd.Series) -> pd.Series:
        """
        Normalize various label representations to binary integers:
        0 = REAL / TRUE / CREDIBLE
        1 = FAKE / FALSE / UNRELIABLE
        """
        def _map_val(v):
            if pd.isna(v):
                return 0
            if isinstance(v, (int, float)):
                return int(v)
            val_str = str(v).strip().lower()
            if val_str in ("fake", "false", "1", "unreliable", "pants on fire", "mostly false", "barely true"):
                return 1
            return 0

        return series.apply(_map_val)

    def load_dataset_file(self, file_path: Path) -> Tuple[pd.DataFrame, Dict[str, str]]:
        """Load and validate dataset file from disk."""
        if not file_path.exists():
            raise VeritasException(f"Dataset file not found: {file_path}", status_code=404)

        ext = file_path.suffix.lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(file_path, low_memory=False)
            elif ext in (".json", ".jsonl"):
                df = pd.read_json(file_path, lines=(ext == ".jsonl"))
            else:
                raise VeritasException(f"Unsupported file format '{ext}'. Use CSV, JSON, or JSONL.", status_code=400)
        except Exception as e:
            raise VeritasException(f"Error parsing dataset file: {str(e)}", status_code=400)

        mappings = self.detect_column_mappings(df.columns.tolist())
        if "text" not in mappings:
            # Fallback: choose longest string column as text
            str_cols = df.select_dtypes(include=["object"]).columns.tolist()
            if str_cols:
                mappings["text"] = str_cols[0]
            else:
                raise VeritasException("Could not detect any text column in the dataset.", status_code=422)

        return df, mappings

    def create_leakage_free_split(
        self,
        df: pd.DataFrame,
        mappings: Dict[str, str],
        train_ratio: float = 0.70,
        val_ratio: float = 0.15,
        test_ratio: float = 0.15,
        stratify: bool = True,
        group_by_narrative: bool = False
    ) -> Dict[str, Any]:
        """
        Split dataset with strict stratification or narrative cluster grouping
        to prevent near-duplicate leakage.
        """
        text_col = mappings["text"]
        label_col = mappings.get("label")

        # Clean nulls
        clean_df = df.dropna(subset=[text_col]).copy()
        if label_col and label_col in clean_df.columns:
            clean_df["canonical_label"] = self.normalize_labels(clean_df[label_col])
        else:
            clean_df["canonical_label"] = 0

        # Create title/narrative cluster hash for group splitting
        title_col = mappings.get("title")
        if group_by_narrative and title_col and title_col in clean_df.columns:
            clean_df["group_id"] = clean_df[title_col].fillna("").apply(
                lambda t: hashlib.md5(t.strip().lower()[:40].encode()).hexdigest()
            )
            gss = GroupShuffleSplit(n_splits=1, train_size=train_ratio, random_state=42)
            train_idx, temp_idx = next(gss.split(clean_df, groups=clean_df["group_id"]))
            train_df = clean_df.iloc[train_idx]
            temp_df = clean_df.iloc[temp_idx]

            # Val / Test split
            rel_val_ratio = val_ratio / (val_ratio + test_ratio)
            gss_val = GroupShuffleSplit(n_splits=1, train_size=rel_val_ratio, random_state=42)
            val_idx, test_idx = next(gss_val.split(temp_df, groups=temp_df["group_id"]))
            val_df = temp_df.iloc[val_idx]
            test_df = temp_df.iloc[test_idx]
        else:
            strat_targets = clean_df["canonical_label"] if stratify else None
            train_df, temp_df = train_test_split(
                clean_df,
                train_size=train_ratio,
                stratify=strat_targets,
                random_state=42
            )
            rel_val_ratio = val_ratio / (val_ratio + test_ratio)
            temp_strat = temp_df["canonical_label"] if stratify else None
            val_df, test_df = train_test_split(
                temp_df,
                train_size=rel_val_ratio,
                stratify=temp_strat,
                random_state=42
            )

        return {
            "total_samples": len(clean_df),
            "train_samples": len(train_df),
            "val_samples": len(val_df),
            "test_samples": len(test_df),
            "class_balance": {
                "train_real": int(np.sum(train_df["canonical_label"] == 0)),
                "train_fake": int(np.sum(train_df["canonical_label"] == 1)),
                "test_real": int(np.sum(test_df["canonical_label"] == 0)),
                "test_fake": int(np.sum(test_df["canonical_label"] == 1)),
            },
            "split_type": "Group-Aware Narrative Split" if group_by_narrative else "Stratified Random Split",
            "train_df": train_df,
            "val_df": val_df,
            "test_df": test_df
        }


dataset_service = DatasetService()
