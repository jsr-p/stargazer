"""
Compatibility layer with results from linearmodels.
"""

from math import sqrt

from linearmodels.iv.results import IVResults, OLSResults
from linearmodels.panel.results import (
    PanelEffectsResults,
    PanelResults,
    RandomEffectsResults,
)

from ..starlib import _extract_feature, _merge_dicts
from . import register_class

# For features that are simple attributes of "model", establish the
# mapping with internal name:
linearmodels_map_base = {
    "p_values": "pvalues",
    "cov_values": "params",
    "cov_std_err": "std_errors",
    "r2": "rsquared",
    "degree_freedom": "df_model",
    "degree_freedom_resid": "df_resid",
    "nobs": "nobs",
}

# Mapping for linearmodels key parameters
# between-, within- and overall-R² values extracted for potential future stats display in Stargazer
# Note: We here use corr_... attributes for the R² as this matches the results obtained in Stata
linear_model_map_panel = {
    "between_r2": "corr_squared_between",
    "within_r2": "corr_squared_within",
    "overall_r2": "corr_squared_overall",
}

# IV specific statistics map
linear_model_map_iv = dict()


def extract_model_data(model):
    data = {}
    if isinstance(model, (PanelEffectsResults, RandomEffectsResults, PanelResults)):
        linearmodels_map = _merge_dicts(linearmodels_map_base, linear_model_map_panel)
        data["ngroups"] = str(int(model.entity_info.total))
    elif isinstance(model, IVResults):
        # TODO: Add support for showing first stage results of IV models
        linearmodels_map = _merge_dicts(linearmodels_map_base, linear_model_map_panel)
        # TODO: Add more relevant statistics for IV models
        data["sargan"] = model.sargan
    elif isinstance(model, OLSResults):
        linearmodels_map = linearmodels_map_base
    else:
        raise ValueError("Unknown model type")

    for key, val in linearmodels_map.items():
        data[key] = _extract_feature(model, val)

    # Common two both FE & IV models
    data["dependent_variable"] = model.summary.tables[0].data[0][1]
    data["cov_names"] = model.params.index.values
    data["conf_int_low_values"] = model.conf_int().lower
    data["conf_int_high_values"] = model.conf_int().upper
    data["resid_std_err"] = sqrt(model.s2)
    data["f_statistic"] = model.f_statistic.stat
    data["f_p_value"] = model.f_statistic.pval
    data["r2_adj"] = None
    data["pseudo_r2"] = None

    return data


classes = [
    (PanelEffectsResults, extract_model_data),
    (RandomEffectsResults, extract_model_data),
    (PanelResults, extract_model_data),
    (IVResults, extract_model_data),
    (OLSResults, extract_model_data),
]

for klass, translator in classes:
    register_class(klass, translator)
