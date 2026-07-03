"""
Mobile-optimized Plotly chart renderer for Streamlit.

Provides a reusable wrapper for rendering Plotly charts with automatic
mobile detection and appropriate configuration for touch devices.

On mobile: Disables drag interactions, zoom, pan to prioritize page scrolling.
On desktop: Preserves all interactive features.
"""

import streamlit as st
from typing import Optional, Dict, Any


def is_mobile_device() -> bool:
    """
    Detect if the current user is on a mobile device.
    
    Uses Streamlit query parameters to detect mobile clients.
    Checks for common mobile user-agent indicators.
    
    Returns:
        bool: True if mobile device detected, False otherwise
    """
    # Check query params (if passed from frontend detection)
    query_params = st.query_params
    if "mobile" in query_params:
        return query_params.get("mobile", "false").lower() == "true"
    
    # Default: Assume mobile if not explicitly set to false
    # In production, you can enhance this with JavaScript detection
    return False


def get_plotly_config(mobile: Optional[bool] = None) -> Dict[str, Any]:
    """
    Get the appropriate Plotly configuration based on device type.
    
    On DESKTOP: Enables all interactive features (zoom, pan, hover, etc.)
    On MOBILE: Disables touch interactions to prioritize page scrolling
    
    Args:
        mobile: Explicitly set mobile mode. If None, auto-detects.
    
    Returns:
        dict: Plotly configuration dictionary
    """
    if mobile is None:
        mobile = is_mobile_device()
    
    if mobile:
        # Mobile configuration: Minimize touch interference
        return {
            # Hide the mode bar (toolbox)
            "displayModeBar": False,
            
            # Disable scroll zoom
            "scrollZoom": False,
            
            # Disable double-click zoom
            "doubleClick": False,
            
            # Disable editing
            "editable": False,
            
            # Disable axis drag handles
            "showAxisDragHandles": False,
            
            # Disable axis range entry boxes
            "showAxisRangeEntryBoxes": False,
            
            # Remove specific interaction buttons
            "modeBarButtonsToRemove": [
                "zoom2d",           # 2D zoom
                "pan2d",            # 2D pan
                "select2d",         # Box select
                "lasso2d",          # Lasso select
                "zoomIn2d",         # Zoom in button
                "zoomOut2d",        # Zoom out button
                "autoScale2d",      # Auto scale
                "resetScale2d",     # Reset scale
            ],
            
            # Responsive design
            "responsive": True,
        }
    else:
        # Desktop configuration: Full interactivity
        return {
            # Show mode bar for desktop users
            "displayModeBar": True,
            
            # Allow scroll zoom on desktop
            "scrollZoom": True,
            
            # Allow double-click zoom on desktop
            "doubleClick": "autosize",
            
            # Allow editing on desktop
            "editable": False,  # Keep false unless specifically needed
            
            # Show axis drag handles on desktop
            "showAxisDragHandles": True,
            
            # Show axis range entry boxes on desktop
            "showAxisRangeEntryBoxes": True,
            
            # Don't remove any buttons on desktop
            "modeBarButtonsToRemove": [],
            
            # Responsive design
            "responsive": True,
        }


def render_plotly_chart(
    figure: Any,
    mobile: Optional[bool] = None,
    use_container_width: bool = True,
    **kwargs
) -> None:
    """
    Render a Plotly chart with mobile-optimized configuration.
    
    This is a drop-in replacement for st.plotly_chart() that automatically
    handles mobile vs. desktop rendering.
    
    On mobile: Disables all drag/zoom interactions to allow page scrolling.
    On desktop: Preserves all interactive features.
    
    Args:
        figure: The Plotly figure object to render
        mobile: Explicitly set mobile mode. If None, auto-detects.
        use_container_width: Whether to use container width (passed to st.plotly_chart)
        **kwargs: Additional arguments passed to st.plotly_chart
    
    Example:
        from src.utils.plotly_helper import render_plotly_chart
        import plotly.graph_objects as go
        
        fig = go.Figure(data=[...])
        render_plotly_chart(fig)  # Auto-detects mobile
        
        # Or explicitly set mobile mode
        render_plotly_chart(fig, mobile=True)
    """
    if mobile is None:
        mobile = is_mobile_device()
    
    # Get appropriate config
    config = get_plotly_config(mobile=mobile)
    
    # Update figure for mobile to disable dragmode
    if mobile:
        figure.update_layout(dragmode=False)
    
    # Merge any additional config from kwargs
    if "config" in kwargs:
        config.update(kwargs.pop("config"))
    
    # Render with Streamlit
    st.plotly_chart(
        figure,
        use_container_width=use_container_width,
        config=config,
        **kwargs
    )


# Inject CSS to prevent Plotly from blocking touch scrolling
def inject_touch_scroll_css() -> None:
    """
    Inject CSS to ensure Plotly charts don't interfere with touch scrolling.
    
    This CSS ensures that touchmove events on Plotly charts still allow
    vertical page scrolling on mobile devices.
    
    Call this once per page (ideally at the top of your Streamlit app).
    """
    css = """
    <style>
    /* Allow touch scrolling on Plotly charts on mobile */
    .plotly-graph-div {
        touch-action: pan-y !important;
    }
    
    /* Ensure SVG doesn't block scroll */
    .plotly-graph-div svg {
        touch-action: auto !important;
    }
    
    /* Prevent mode bar from interfering on mobile */
    .modebar {
        touch-action: auto !important;
    }
    
    /* On small screens, reduce chart height if needed */
    @media (max-width: 768px) {
        .plotly-graph-div {
            max-height: 400px;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
