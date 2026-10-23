#ifndef slic3r_PrefectWorkflowPreferences_hpp_
#define slic3r_PrefectWorkflowPreferences_hpp_

#include <initializer_list>

namespace Slic3r { namespace Prefect {

// Kept independent of wxWidgets so upgrade behaviour can be tested against
// stored preference values without starting the GUI or a physical printer.
template<class Config> void set_workflow_defaults(Config& config)
{
    for (const char* key : {"background_processing", "prefect_auto_sync_filaments",
                            "prefect_click_filament_assigns_selection", "prefect_printer_collapsed",
                            "prefect_import_separate_objects", "prefect_hide_tips",
                            "prefect_suppress_tpu_cold_pull", "prefect_support_interface_menu",
                            "prefect_arrange_rotation", "prefect_arrange_after_import"}) {
        if (config.get(key).empty())
            config.set_bool(key, true);
    }
    if (config.get("prefect_simple_fields_enabled").empty())
        config.set_bool("prefect_simple_fields_enabled", false);
    if (config.get("prefect_workflow_revision").empty())
        config.set("prefect_workflow_revision", "2");
}

template<class Config> bool migrate_workflow_preferences(Config& config, bool file_has_revision)
{
    // A copied stock profile may explicitly disable background slicing. The
    // revision records installation of defaults, not permission to reset a choice.
    if (file_has_revision && config.get("prefect_workflow_revision") != "1")
        return false;
    config.set("prefect_workflow_revision", "2");
    return true;
}

}} // namespace Slic3r::Prefect

#endif
