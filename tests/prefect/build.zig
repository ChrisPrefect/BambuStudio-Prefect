const std = @import("std");

// Optional low-memory Windows test runner: zig build -j1
// Independent of the full Bambu Studio CMake/wxWidgets build.
pub fn build(b: *std.Build) void {
    const target = b.standardTargetOptions(.{});
    const optimize = b.standardOptimizeOption(.{});
    const tests = [_][]const u8{ "arrange", "background", "filament_sync", "preferences", "simple_fields", "workflow", "notification_tips", "helio_ads", "plate_clear" };
    for (tests) |name| {
        const executable = b.addExecutable(.{
            .name = name,
            .target = target,
            .optimize = optimize,
        });
        executable.addCSourceFile(.{
            .file = b.path(b.fmt("{s}_test.cpp", .{name})),
            // Zig ReleaseFast otherwise defines NDEBUG for C/C++ translation
            // units. These regression executables must retain assert checks.
            .flags = &.{ "-std=c++17", "-UNDEBUG", "-Wall", "-Wextra", "-Werror", "-pedantic" },
        });
        executable.linkLibCpp();
        executable.linkLibC();
        const run = b.addRunArtifact(executable);
        b.default_step.dependOn(&run.step);
    }
}
