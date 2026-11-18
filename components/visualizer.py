"""
Smart Retail Sales Analytics & Visualization System
Interactive Plotly Visualizer Engine
Generates styled Plotly charts with generous margins to prevent title/legend collisions.
Features specialized GIS India Store Map (Positron, Dark Matter, OpenStreetMap, Vector) and World Map visualizers.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any

CHART_THEME = "plotly_white"
DEFAULT_COLORS = [
    "#1E3A8A", "#2563EB", "#0D9488", "#10B981", 
    "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", 
    "#14B8A6", "#F97316", "#06B6D4", "#84CC16"
]

REGION_COLORS = {
    "South": "#2563EB",    # Royal Blue
    "West": "#F59E0B",     # Amber
    "North": "#10B981",    # Emerald
    "East": "#8B5CF6",     # Violet
    "Central": "#0D9488"   # Teal
}

STORE_TYPE_COLORS = {
    "Flagship": "#1E3A8A",
    "Superstore": "#2563EB",
    "Hypermarket": "#0D9488",
    "Express Mart": "#10B981",
    "Mall Outlet": "#F59E0B"
}

class ChartVisualizer:
    """Builds interactive, publication-ready Plotly figures with proper spacing and responsive layout."""

    @staticmethod
    def _apply_layout_defaults(
        fig: go.Figure, 
        title: str, 
        height: int = 460, 
        show_legend: bool = True,
        legend_position: str = "top" # 'top', 'bottom', 'none'
    ) -> go.Figure:
        """Applies consistent typography, generous top margin, and non-overlapping legend formatting."""
        
        if legend_position == "bottom":
            margin = dict(l=55, r=35, t=70, b=80)
            legend_layout = dict(
                orientation="h",
                yanchor="top",
                y=-0.18,
                xanchor="center",
                x=0.5,
                font=dict(size=11, family="Inter, sans-serif")
            )
        elif legend_position == "top" and show_legend:
            margin = dict(l=55, r=35, t=90, b=50)
            legend_layout = dict(
                orientation="h",
                yanchor="bottom",
                y=1.04,
                xanchor="right",
                x=1.0,
                font=dict(size=11, family="Inter, sans-serif")
            )
        else:
            margin = dict(l=55, r=35, t=65, b=50)
            legend_layout = dict()

        fig.update_layout(
            template=CHART_THEME,
            title={
                "text": f"<b>{title}</b>",
                "font": {"size": 15, "family": "Inter, Roboto, sans-serif", "color": "#0F172A"},
                "x": 0.01,
                "y": 0.98,
                "xanchor": "left",
                "yanchor": "top"
            },
            height=height,
            margin=margin,
            hovermode="closest",
            showlegend=show_legend and legend_position != "none",
            legend=legend_layout if show_legend and legend_position != "none" else None,
            font=dict(family="Inter, Roboto, sans-serif", color="#334155")
        )
        return fig

    @classmethod
    def line_chart(
        cls, 
        df: pd.DataFrame, 
        x: str, 
        y: str or List[str], 
        title: str, 
        color: Optional[str] = None,
        height: int = 460
    ) -> go.Figure:
        """Interactive line chart with markers, non-overlapping legend, and clean grid."""
        fig = px.line(
            df, x=x, y=y, color=color,
            color_discrete_sequence=DEFAULT_COLORS,
            markers=True
        )
        fig.update_traces(line=dict(width=2.5), marker=dict(size=5))
        fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", tickangle=-25)
        fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        return cls._apply_layout_defaults(fig, title, height=height, legend_position="top")

    @classmethod
    def bar_chart(
        cls, 
        df: pd.DataFrame, 
        x: str, 
        y: str, 
        title: str, 
        color: Optional[str] = None,
        orientation: str = "v",
        barmode: str = "relative",
        text_auto: bool = True,
        height: int = 460
    ) -> go.Figure:
        """Interactive bar chart (vertical or horizontal) with legible labels."""
        show_leg = bool(color is not None and color != x and color != y)
        fig = px.bar(
            df, x=x, y=y, color=color,
            orientation=orientation,
            barmode=barmode,
            color_discrete_sequence=DEFAULT_COLORS,
            text_auto=".2s" if text_auto else False
        )
        if orientation == "v":
            fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", tickangle=-20)
            fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        else:
            fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9")
            fig.update_yaxes(showgrid=False)
            
        return cls._apply_layout_defaults(fig, title, height=height, show_legend=show_leg, legend_position="top")

    @classmethod
    def pie_chart(
        cls, 
        df: pd.DataFrame, 
        names: str, 
        values: str, 
        title: str, 
        hole: float = 0.52,
        height: int = 450
    ) -> go.Figure:
        """Donut or Pie chart with clear separation between title and pie."""
        fig = px.pie(
            df, names=names, values=values,
            hole=hole,
            color_discrete_sequence=DEFAULT_COLORS
        )
        fig.update_traces(
            textposition="inside",
            textinfo="percent+label",
            marker=dict(line=dict(color="#FFFFFF", width=2))
        )
        return cls._apply_layout_defaults(fig, title, height=height, legend_position="bottom")

    @classmethod
    def area_chart(
        cls, 
        df: pd.DataFrame, 
        x: str, 
        y: str, 
        title: str, 
        color: Optional[str] = None,
        height: int = 460
    ) -> go.Figure:
        """Area chart with continuous gradient and clean margins."""
        fig = px.area(
            df, x=x, y=y, color=color,
            color_discrete_sequence=DEFAULT_COLORS
        )
        fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9", tickangle=-25)
        fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        return cls._apply_layout_defaults(fig, title, height=height, legend_position="top")

    @classmethod
    def heatmap(
        cls, 
        df: pd.DataFrame, 
        x: str, 
        y: str, 
        z: str, 
        title: str, 
        colorscale: str = "Blues",
        height: int = 480
    ) -> go.Figure:
        """2D Heatmap with generous title spacing."""
        pivot_table = df.pivot(index=y, columns=x, values=z).fillna(0)
        fig = px.imshow(
            pivot_table,
            text_auto=".2s",
            aspect="auto",
            color_continuous_scale=colorscale,
            labels=dict(x=x, y=y, color=z)
        )
        return cls._apply_layout_defaults(fig, title, height=height, show_legend=False)

    @classmethod
    def correlation_heatmap(cls, corr_df: pd.DataFrame, title: str = "Feature Correlation Matrix", height: int = 460) -> go.Figure:
        """Correlation heatmap with annotated values."""
        fig = px.imshow(
            corr_df,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1
        )
        return cls._apply_layout_defaults(fig, title, height=height, show_legend=False)

    @classmethod
    def scatter_plot(
        cls, 
        df: pd.DataFrame, 
        x: str, 
        y: str, 
        title: str, 
        color: Optional[str] = None,
        size: Optional[str] = None,
        hover_name: Optional[str] = None,
        height: int = 470
    ) -> go.Figure:
        """Scatter/Bubble plot with responsive hover."""
        fig = px.scatter(
            df, x=x, y=y, color=color, size=size,
            hover_name=hover_name,
            color_discrete_sequence=DEFAULT_COLORS
        )
        fig.update_traces(marker=dict(opacity=0.85, line=dict(width=1, color="#FFFFFF")))
        fig.update_xaxes(showgrid=True, gridcolor="#F1F5F9")
        fig.update_yaxes(showgrid=True, gridcolor="#F1F5F9")
        return cls._apply_layout_defaults(fig, title, height=height, legend_position="top")

    @classmethod
    def india_store_map(
        cls, 
        store_df: pd.DataFrame, 
        title: str = "🇮🇳 India Multi-Region Retail Store Network & Sales Distribution",
        map_style: str = "carto-positron", # 'carto-positron', 'open-street-map', 'carto-darkmatter', 'vector'
        color_by: str = "Profit Margin", # 'Profit Margin', 'Region', 'Store Type'
        size_by: str = "Revenue", # 'Revenue', 'Orders'
        center_lat: float = 21.8,
        center_lon: float = 79.5,
        zoom: float = 4.3,
        height: int = 720
    ) -> go.Figure:
        """
        State-of-the-art GIS Interactive Map for Indian Retail Operations.
        Features dual-layer glowing store halos, detailed basemaps (Positron/Dark/OSM/Vector),
        custom tooltips, and interactive multi-region filters.
        """
        valid_df = store_df.dropna(subset=["Latitude", "Longitude"]).copy()
        if valid_df.empty:
            return go.Figure()

        # Build custom hover columns
        for c in ["Store Name", "City", "State", "Region", "Store Type", "Revenue", "Profit", "Profit Margin", "Orders", "Avg_Order_Value"]:
            if c not in valid_df.columns:
                valid_df[c] = 0

        # Calculate bubble sizes
        size_vals = valid_df[size_by] if size_by in valid_df.columns else valid_df["Revenue"]
        min_size, max_size = size_vals.min(), size_vals.max()
        if min_size == max_size:
            scaled_sizes = np.full(len(valid_df), 22)
            halo_sizes = np.full(len(valid_df), 42)
        else:
            scaled_sizes = np.interp(size_vals, (min_size, max_size), (15, 38))
            halo_sizes = np.interp(size_vals, (min_size, max_size), (32, 70))

        valid_df["_scaled_size"] = scaled_sizes
        valid_df["_halo_size"] = halo_sizes

        fig = go.Figure()

        # Determine plotting engine: Scattermap (Plotly 6+) vs Scattermapbox (Plotly 5) vs Scattergeo
        has_scattermap = hasattr(go, "Scattermap")
        is_vector = (map_style == "vector")

        if not is_vector:
            # === PROFESSIONAL TILE-BASED GIS MAP (Carto Positron, Dark Matter, or OSM) ===
            map_cls = go.Scattermap if has_scattermap else getattr(go, "Scattermapbox", go.Scattergeo)

            # Layer 1: Semi-transparent regional footprint halo
            fig.add_trace(map_cls(
                lat=valid_df["Latitude"],
                lon=valid_df["Longitude"],
                mode="markers",
                marker=dict(
                    size=valid_df["_halo_size"],
                    color="rgba(37, 99, 235, 0.22)" if map_style != "carto-darkmatter" else "rgba(59, 130, 246, 0.28)",
                    allowoverlap=True
                ),
                hoverinfo="skip",
                showlegend=False,
                name="Store Radius"
            ))

            # Layer 2: Core Store Pin
            if color_by == "Profit Margin":
                fig.add_trace(map_cls(
                    lat=valid_df["Latitude"],
                    lon=valid_df["Longitude"],
                    mode="markers+text",
                    text=valid_df["City"],
                    textposition="top right",
                    textfont=dict(
                        family="Inter, sans-serif", 
                        size=11, 
                        color="#0F172A" if map_style != "carto-darkmatter" else "#F8FAFC"
                    ),
                    marker=dict(
                        size=valid_df["_scaled_size"],
                        color=valid_df["Profit Margin"],
                        colorscale="Viridis",
                        colorbar=dict(
                            title=dict(text="<b>Profit Margin %</b>", font=dict(size=12)),
                            thickness=16,
                            len=0.65,
                            x=0.98,
                            y=0.5,
                            ticksuffix="%",
                            bgcolor="rgba(255, 255, 255, 0.85)" if map_style != "carto-darkmatter" else "rgba(15, 23, 42, 0.85)",
                            outlinecolor="#CBD5E1"
                        ),
                        showscale=True,
                        opacity=0.95,
                        allowoverlap=True
                    ),
                    customdata=valid_df[["Store Name", "City", "State", "Region", "Store Type", "Revenue", "Profit", "Profit Margin", "Orders", "Avg_Order_Value"]].values,
                    hovertemplate=(
                        "<div style='font-family: Inter, sans-serif; padding: 4px;'>"
                        "<b style='font-size: 14px; color: #1E3A8A;'>🏬 %{customdata[0]}</b><br>"
                        "<span style='color: #64748B;'>📍 %{customdata[1]}, %{customdata[2]} (%{customdata[3]} Region)</span><br>"
                        "🏷️ Store Format: <b>%{customdata[4]}</b><hr style='margin: 4px 0; border: 0.5px solid #E2E8F0;'>"
                        "💰 Total Store Sales: <b style='color: #059669;'>₹%{customdata[5]:,.2f}</b><br>"
                        "📈 Net Gross Profit: <b>₹%{customdata[6]:,.2f}</b><br>"
                        "📊 Operating Margin: <b style='color: #2563EB;'>%{customdata[7]:.2f}%</b><br>"
                        "📦 Total Transactions: <b>%{customdata[8]:,} orders</b><br>"
                        "🛍️ Average Spend (AOV): <b>₹%{customdata[9]:,.2f}</b>"
                        "</div><extra></extra>"
                    ),
                    name="Retail Stores"
                ))

            else:
                # Group by Region or Store Type for interactive legend
                group_col = "Region" if color_by == "Region" else "Store Type"
                palette = REGION_COLORS if group_col == "Region" else STORE_TYPE_COLORS

                for grp_name in sorted(valid_df[group_col].dropna().unique()):
                    grp_df = valid_df[valid_df[group_col] == grp_name]
                    grp_color = palette.get(grp_name, "#2563EB")

                    fig.add_trace(map_cls(
                        lat=grp_df["Latitude"],
                        lon=grp_df["Longitude"],
                        mode="markers+text",
                        text=grp_df["City"],
                        textposition="top right",
                        textfont=dict(
                            family="Inter, sans-serif", 
                            size=11, 
                            color="#0F172A" if map_style != "carto-darkmatter" else "#F8FAFC"
                        ),
                        marker=dict(
                            size=grp_df["_scaled_size"],
                            color=grp_color,
                            opacity=0.92,
                            allowoverlap=True
                        ),
                        name=f"{grp_name} ({len(grp_df)} Stores)",
                        customdata=grp_df[["Store Name", "City", "State", "Region", "Store Type", "Revenue", "Profit", "Profit Margin", "Orders", "Avg_Order_Value"]].values,
                        hovertemplate=(
                            "<div style='font-family: Inter, sans-serif; padding: 4px;'>"
                            "<b style='font-size: 14px; color: #1E3A8A;'>🏬 %{customdata[0]}</b><br>"
                            "<span style='color: #64748B;'>📍 %{customdata[1]}, %{customdata[2]} (%{customdata[3]} Region)</span><br>"
                            "🏷️ Store Format: <b>%{customdata[4]}</b><hr style='margin: 4px 0; border: 0.5px solid #E2E8F0;'>"
                            "💰 Total Store Sales: <b style='color: #059669;'>₹%{customdata[5]:,.2f}</b><br>"
                            "📈 Net Gross Profit: <b>₹%{customdata[6]:,.2f}</b><br>"
                            "📊 Operating Margin: <b style='color: #2563EB;'>%{customdata[7]:.2f}%</b><br>"
                            "📦 Total Transactions: <b>%{customdata[8]:,} orders</b><br>"
                            "🛍️ Average Spend (AOV): <b>₹%{customdata[9]:,.2f}</b>"
                            "</div><extra></extra>"
                        )
                    ))

            # Apply map layout configuration
            if has_scattermap:
                fig.update_layout(
                    map_style=map_style,
                    map=dict(
                        center=dict(lat=center_lat, lon=center_lon),
                        zoom=zoom
                    )
                )
            else:
                fig.update_layout(
                    mapbox_style=map_style,
                    mapbox=dict(
                        center=dict(lat=center_lat, lon=center_lon),
                        zoom=zoom
                    )
                )

        else:
            # === OFFLINE VECTOR MAP (Scattergeo) ===
            fig.add_trace(go.Scattergeo(
                lat=valid_df["Latitude"],
                lon=valid_df["Longitude"],
                mode="markers+text",
                text=valid_df["City"],
                textposition="top center",
                textfont=dict(family="Inter, sans-serif", size=10, color="#1E293B"),
                marker=dict(
                    size=valid_df["_scaled_size"],
                    color=valid_df["Profit Margin"],
                    colorscale="Viridis",
                    colorbar=dict(title="Profit Margin %", thickness=14, len=0.65, x=0.98),
                    showscale=True,
                    opacity=0.92,
                    line=dict(width=1.5, color="#FFFFFF")
                ),
                customdata=valid_df[["Store Name", "City", "State", "Region", "Store Type", "Revenue", "Profit", "Profit Margin", "Orders", "Avg_Order_Value"]].values,
                hovertemplate=(
                    "<b>🏬 %{customdata[0]}</b><br>"
                    "📍 %{customdata[1]}, %{customdata[2]}<br>"
                    "💰 Sales: <b>₹%{customdata[5]:,.2f}</b><br>"
                    "📊 Margin: <b>%{customdata[7]:.2f}%</b><extra></extra>"
                ),
                name="Retail Stores"
            ))

            fig.update_geos(
                center=dict(lat=center_lat, lon=center_lon),
                projection_scale=5.2,
                visible=True,
                resolution=50,
                showcountries=True,
                countrycolor="#64748B",
                showsubunits=True,
                subunitcolor="#CBD5E1",
                showland=True,
                landcolor="#F1F5F9",
                showocean=True,
                oceancolor="#E0F2FE"
            )

        fig.update_layout(
            template=CHART_THEME,
            title={
                "text": f"<b>{title}</b>",
                "font": {"size": 15, "family": "Inter, Roboto, sans-serif", "color": "#0F172A"},
                "x": 0.01,
                "y": 0.98,
                "xanchor": "left",
                "yanchor": "top"
            },
            height=height,
            margin=dict(l=10, r=10, t=55, b=10),
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.03,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(255, 255, 255, 0.9)",
                bordercolor="#E2E8F0",
                borderwidth=1,
                font=dict(size=11, family="Inter, sans-serif")
            ) if color_by != "Profit Margin" else None
        )

        return fig

    @classmethod
    def world_store_map(
        cls, 
        store_df: pd.DataFrame, 
        title: str = "🌍 Global Geographic Retail Distribution & International Markets",
        height: int = 620
    ) -> go.Figure:
        """Global interactive map view showing international presence and shipments."""
        valid_df = store_df.dropna(subset=["Latitude", "Longitude"]).copy()

        fig = px.scatter_geo(
            valid_df,
            lat="Latitude",
            lon="Longitude",
            hover_name="Store Name" if "Store Name" in valid_df.columns else "City",
            size="Revenue",
            color="Region" if "Region" in valid_df.columns else "Profit Margin",
            color_discrete_sequence=DEFAULT_COLORS,
            projection="natural earth",
            size_max=32
        )
        fig.update_geos(
            showcountries=True,
            countrycolor="#94A3B8",
            showland=True,
            landcolor="#F8FAFC",
            showocean=True,
            oceancolor="#EFF6FF",
            showcoastlines=True,
            coastlinecolor="#CBD5E1"
        )
        return cls._apply_layout_defaults(fig, title, height=height, legend_position="bottom")

    @classmethod
    def pareto_chart(cls, pareto_df: pd.DataFrame, top_n: int = 15, title: str = "Pareto Analysis: 80/20 Rule", height: int = 470) -> go.Figure:
        """Dual-axis chart with product revenue bars and cumulative percentage line with proper margin."""
        sub_df = pareto_df.head(top_n)
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=sub_df["Product Name"],
            y=sub_df["Revenue"],
            name="Product Revenue (₹)",
            marker_color="#2563EB",
            yaxis="y"
        ))

        fig.add_trace(go.Scatter(
            x=sub_df["Product Name"],
            y=sub_df["Cumulative_Percentage"],
            name="Cumulative %",
            marker_color="#EF4444",
            line=dict(width=2.5),
            yaxis="y2"
        ))

        fig.add_hline(y=80, line_dash="dash", line_color="#10B981", annotation_text="80% Threshold", yref="y2")

        fig.update_layout(
            yaxis=dict(title="Revenue (₹)", showgrid=True, gridcolor="#F1F5F9"),
            yaxis2=dict(title="Cumulative %", overlaying="y", side="right", range=[0, 105], showgrid=False)
        )
        return cls._apply_layout_defaults(fig, title, height=height, legend_position="top")

    @classmethod
    def forecast_chart(cls, forecast_df: pd.DataFrame, title: str = "Sales Forecast: Actual vs Predicted", height: int = 480) -> go.Figure:
        """Line chart clearly separating Actual historical sales from Predicted future values with confidence bands."""
        fig = go.Figure()

        actual_df = forecast_df[forecast_df["Data_Type"] == "Actual"]
        pred_df = forecast_df[forecast_df["Data_Type"] == "Forecast (Predicted)"]

        fig.add_trace(go.Scatter(
            x=actual_df["Order Date"],
            y=actual_df["Revenue"],
            name="Actual Historical Sales",
            mode="lines",
            line=dict(color="#1E3A8A", width=2.5)
        ))

        fig.add_trace(go.Scatter(
            x=pred_df["Order Date"],
            y=pred_df["Upper_Bound"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ))

        fig.add_trace(go.Scatter(
            x=pred_df["Order Date"],
            y=pred_df["Lower_Bound"],
            mode="lines",
            line=dict(width=0),
            fill="tonexty",
            fillcolor="rgba(245, 158, 11, 0.22)",
            name="80% Confidence Interval"
        ))

        fig.add_trace(go.Scatter(
            x=pred_df["Order Date"],
            y=pred_df["Revenue"],
            name="ML Predicted Forecast",
            mode="lines+markers",
            line=dict(color="#F59E0B", width=3, dash="dot"),
            marker=dict(size=4)
        ))

        return cls._apply_layout_defaults(fig, title, height=height, legend_position="top")
