#include "../../src/slic3r/GUI/PrefectHelioAdsPolicy.hpp"

#include <cassert>
#include <initializer_list>
#include <iostream>

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

int main()
{
    using namespace Slic3r::Prefect;
    assert(hide_helio_ads(""));
    assert(hide_helio_ads("true"));
    assert(!hide_helio_ads("false"));

    // An advertising preference must never switch off a user's enabled analysis.
    for (bool hide_ads : {false, true}) {
        for (bool enabled : {false, true}) {
            const auto toolbar = helio_toolbar_visibility(hide_ads, enabled);
            assert(toolbar.enabled_analysis == enabled);
            assert(toolbar.activation_offer == !hide_ads);
            assert(toolbar.any() == (enabled || !hide_ads));
        }
    }

    // Global tips and Helio advertising are independent. Blocking advertising
    // keeps useful general tips available during a deliberate Helio operation.
    for (bool hide_ads : {false, true}) {
        for (bool helio_process : {false, true}) {
            assert(daily_tip_source(true, hide_ads, helio_process) == DailyTipSource::None);
        }
    }
    assert(daily_tip_source(false, false, false) == DailyTipSource::General);
    assert(daily_tip_source(false, false, true) == DailyTipSource::Helio);
    assert(daily_tip_source(false, true, false) == DailyTipSource::General);
    assert(daily_tip_source(false, true, true) == DailyTipSource::General);

    // Turning ads off/on during an enabled operation must be reversible without
    // resetting the service state or losing its existing result/action entry.
    for (bool hide_ads : {false, true, false, true}) {
        assert(helio_toolbar_visibility(hide_ads, true).enabled_analysis);
        assert(daily_tip_source(false, hide_ads, true) ==
               (hide_ads ? DailyTipSource::General : DailyTipSource::Helio));
    }
    std::cout << "Helio promotion visibility: all regression checks passed\n";
}
