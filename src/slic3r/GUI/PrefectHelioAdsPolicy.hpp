#ifndef slic3r_GUI_PrefectHelioAdsPolicy_hpp_
#define slic3r_GUI_PrefectHelioAdsPolicy_hpp_

#include <string>

namespace Slic3r { namespace Prefect {

// Missing values use the fork default even while a new profile is initialized.
inline bool hide_helio_ads(const std::string& stored_value)
{
    return stored_value != "false";
}

struct HelioToolbarVisibility {
    bool activation_offer;
    bool enabled_analysis;
    bool any() const { return activation_offer || enabled_analysis; }
};

inline HelioToolbarVisibility helio_toolbar_visibility(bool hide_ads, bool helio_enabled)
{
    return { !hide_ads, helio_enabled };
}

enum class DailyTipSource { None, General, Helio };

inline DailyTipSource daily_tip_source(bool hide_tips, bool hide_ads, bool helio_process)
{
    if (hide_tips)
        return DailyTipSource::None;
    return helio_process && !hide_ads ? DailyTipSource::Helio : DailyTipSource::General;
}

}} // namespace Slic3r::Prefect

#endif
