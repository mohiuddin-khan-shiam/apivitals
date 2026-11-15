"""ApiVitals: The living health radar, latency benchmark, and curated directory of free public APIs."""

from apivitals.loader import load_catalog
from apivitals.models import ApiCatalog, ApiDefinition, HealthProbeResult, ServiceStatus
from apivitals.prober import probe_api, probe_catalog

__version__ = "0.1.0"
__all__ = [
    "__version__",
    "ApiCatalog",
    "ApiDefinition",
    "HealthProbeResult",
    "ServiceStatus",
    "load_catalog",
    "probe_api",
    "probe_catalog",
]
