#include "../../src/libslic3r/PrefectWorkflow.hpp"

#include <cassert>
#include <iostream>

#ifdef NDEBUG
#error "Policy regression tests require active assertions (compile with -UNDEBUG)."
#endif

int main()
{
    using Slic3r::PrefectWorkflow::suppress_tpu_cold_pull;
    constexpr auto cold_pull = "Please cold pull before printing TPU to avoid clogging. You may use cold pull maintenance on the printer.";
    assert(suppress_tpu_cold_pull(true, "warning", cold_pull));
    assert(!suppress_tpu_cold_pull(false, "warning", cold_pull));
    assert(!suppress_tpu_cold_pull(true, "prohibition", cold_pull));
    assert(!suppress_tpu_cold_pull(true, "error", cold_pull));
    assert(!suppress_tpu_cold_pull(true, "warning", "TPU is not supported by AMS."));
    assert(!suppress_tpu_cold_pull(true, "warning", "How to feed TPU filament."));
    assert(!suppress_tpu_cold_pull(true, "warning", "A new upstream TPU message"));
    assert(!suppress_tpu_cold_pull(true, "warning", ""));
    std::cout << "Cold-pull reminder policy: all regression checks passed\n";
}
