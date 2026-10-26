#ifndef slic3r_GUI_PrefectArrangePolicy_hpp_
#define slic3r_GUI_PrefectArrangePolicy_hpp_

#include <cstddef>
#include <initializer_list>
#include <string>

namespace Slic3r { namespace GUI { namespace Prefect {

// Older fork versions forced rotation on without updating the hidden per-mode
// values. Transfer that effective choice once; subsequent explicit choices win.
template<class Config> bool migrate_arrange_rotation_defaults(Config& config)
{
    const char* marker = "prefect_arrange_rotation_default_revision";
    if (!config.get(marker).empty())
        return false;
    if (config.get_bool("prefect_arrange_rotation")) {
        for (const char* key : {"enable_rotation_fff", "enable_rotation_fff_seq_print", "enable_rotation_sla"})
            config.set("arrange", key, std::string("1"));
    }
    config.set(marker, "1");
    return true;
}

inline bool initial_arrange_rotation(const std::string& stored_value, bool default_enabled)
{
    if (stored_value.empty())
        return default_enabled;
    return stored_value == "1" || stored_value == "yes" || stored_value == "true";
}

inline bool manual_arrange_available(bool has_objects, bool ui_job_running, bool closing)
{
    // The normal Arrange job stops background slicing in before_start().
    // Background slicing must not silently veto a manual toolbar request.
    return has_objects && !ui_job_running && !closing;
}

inline bool arrange_toolbar_enabled(bool can_arrange, bool popup_open)
{
    // A running job must not clear the toolbar's pressed state and close the
    // options popup. Its controls are disabled until another job can start.
    return can_arrange || popup_open;
}

inline bool arrange_on_toolbar_open(bool enabled, bool popup_open, bool can_arrange)
{
    // The toolbar callback also runs when toggling an item off. Closing the
    // popup must never arrange, and a busy worker must never receive a retry.
    return enabled && popup_open && can_arrange;
}

inline bool preserve_arrange_popup_on_click(bool enabled, bool direct_left_click, const std::string& item_name)
{
    return enabled && direct_left_click && item_name == "arrange";
}

inline bool auto_arrange_insertion_eligible(bool enabled, std::size_t inserted_objects, bool preserve_layout)
{
    return enabled && inserted_objects > 1 && !preserve_layout;
}

enum class PendingArrangeAction { Stop, Retry, Arrange };

struct PendingArrangeState
{
    bool enabled;
    bool closing;
    bool editable;
    bool same_model;
    bool same_objects;
    bool same_undo_position;
    bool busy;
};

inline PendingArrangeAction pending_arrange_action(const PendingArrangeState &state)
{
    // Invalidated requests must stop even while another operation is busy.
    if (!state.enabled || state.closing || !state.editable || !state.same_model ||
        !state.same_objects || !state.same_undo_position)
        return PendingArrangeAction::Stop;
    return state.busy ? PendingArrangeAction::Retry : PendingArrangeAction::Arrange;
}

}}} // namespace Slic3r::GUI::Prefect
#endif
