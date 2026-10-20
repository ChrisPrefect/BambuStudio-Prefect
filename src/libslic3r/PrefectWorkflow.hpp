#ifndef slic3r_PrefectWorkflow_hpp_
#define slic3r_PrefectWorkflow_hpp_

#include <string_view>

namespace Slic3r { namespace PrefectWorkflow {

// Match the upstream, untranslated message and severity, never its translated
// presentation. In particular, a future prohibition must not become dismissible.
inline bool suppress_tpu_cold_pull(bool enabled, std::string_view action, std::string_view description)
{
    return enabled && action == "warning" && description ==
        "Please cold pull before printing TPU to avoid clogging. You may use cold pull maintenance on the printer.";
}

}} // namespace Slic3r::PrefectWorkflow

#endif
