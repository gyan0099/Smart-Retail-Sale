"""
Smart Retail Sales Analytics & Visualization System
Machine Learning: Customer Segmentation via K-Means Clustering
Segments customers based on RFM features with PCA projection and persona profiling.
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score

class CustomerClusterer:
    """Unsupervised Machine Learning model for data-driven customer behavioral segmentation."""

    @staticmethod
    def cluster_customers(
        rfm_df: pd.DataFrame, 
        n_clusters: int = 4
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Fits K-Means on normalized Recency, Frequency, and Monetary features.
        Returns:
            clustered_df: DataFrame with assigned cluster labels, PCA coordinates, and Persona names
            metrics: Dict with Silhouette Score, Inertia, and Cluster Profiles
        """
        if rfm_df.empty or len(rfm_df) < n_clusters:
            return pd.DataFrame(), {}

        features = ["Recency", "Frequency", "Monetary"]
        X = rfm_df[features].copy()

        # Handle log transforms for skewed monetary/frequency
        X["Log_Recency"] = np.log1p(X["Recency"])
        X["Log_Frequency"] = np.log1p(X["Frequency"])
        X["Log_Monetary"] = np.log1p(X["Monetary"])

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X[["Log_Recency", "Log_Frequency", "Log_Monetary"]])

        # Evaluate silhouette score across range
        scores = {}
        for k in range(2, min(7, len(rfm_df))):
            km_test = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels_test = km_test.fit_predict(X_scaled)
            scores[k] = round(float(silhouette_score(X_scaled, labels_test)), 3)

        # Fit model with chosen clusters
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X_scaled)
        
        # 2D PCA projection for visualization
        pca = PCA(n_components=2, random_state=42)
        pca_coords = pca.fit_transform(X_scaled)

        result_df = rfm_df.copy()
        result_df["Cluster"] = cluster_labels
        result_df["PCA1"] = pca_coords[:, 0].round(2)
        result_df["PCA2"] = pca_coords[:, 1].round(2)

        # Generate Persona Profiles based on centroid metrics
        cluster_summary = result_df.groupby("Cluster").agg(
            Recency_Mean=("Recency", "mean"),
            Frequency_Mean=("Frequency", "mean"),
            Monetary_Mean=("Monetary", "mean"),
            Customer_Count=("Customer ID", "count")
        ).reset_index()

        # Persona Naming heuristic
        def name_cluster(row):
            rec = row["Recency_Mean"]
            freq = row["Frequency_Mean"]
            mon = row["Monetary_Mean"]

            if mon >= cluster_summary["Monetary_Mean"].median() and freq >= cluster_summary["Frequency_Mean"].median():
                return "Platinum VIP Champions"
            elif rec <= cluster_summary["Recency_Mean"].median() and freq <= cluster_summary["Frequency_Mean"].median():
                return "Promising Newcomers"
            elif rec > cluster_summary["Recency_Mean"].median() and freq > cluster_summary["Frequency_Mean"].median():
                return "At-Risk Loyalists"
            else:
                return "Dormant / Low-Engagement"

        persona_map = {row["Cluster"]: name_cluster(row) for _, row in cluster_summary.iterrows()}
        result_df["Cluster_Persona"] = result_df["Cluster"].map(persona_map)
        cluster_summary["Persona"] = cluster_summary["Cluster"].map(persona_map)

        current_silhouette = round(float(silhouette_score(X_scaled, cluster_labels)), 3)

        metrics = {
            "chosen_k": n_clusters,
            "silhouette_score": current_silhouette,
            "inertia": round(float(kmeans.inertia_), 2),
            "silhouette_by_k": scores,
            "cluster_profiles": cluster_summary,
            "pca_variance_ratio": [round(float(v), 3) for v in pca.explained_variance_ratio_]
        }

        return result_df, metrics
