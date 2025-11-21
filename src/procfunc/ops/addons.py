import logging

import addon_utils
import bpy

logger = logging.getLogger(__name__)


def require_blender_addon(addon: str, fail: str = "fatal", allow_online=False):
    def report_fail(msg):
        if fail == "warn":
            logger.warning(
                msg + ". Generation may crash at runtime if certain assets are used."
            )
        elif fail == "fatal":
            raise ValueError(msg)
        else:
            raise ValueError(
                f"{require_blender_addon.__name__} got unrecognized {fail=}"
            )

    long = f"bl_ext.blender_org.{addon}"

    addon_present = long in bpy.context.preferences.addons.keys()

    if addon_present:
        logger.debug(f"Addon {addon} already present.")
        return True

    builtin_local_addons = set(a.__name__ for a in addon_utils.modules(refresh=True))

    if (
        (addon not in builtin_local_addons)
        and (long not in builtin_local_addons)
        and (not allow_online)
    ):
        report_fail(f"{addon=} not found and online install is disabled")

    try:
        if long in builtin_local_addons:
            logger.info(
                f"Addon {addon} already in blender local addons, attempt to enable it."
            )
            bpy.ops.preferences.addon_enable(module=long)
        else:
            bpy.ops.extensions.userpref_allow_online()
            logger.info(f"Installing Add-on {addon}.")
            bpy.ops.extensions.repo_sync(repo_index=0)
            bpy.ops.extensions.package_install(
                repo_index=0, pkg_id=addon, enable_on_install=True
            )
            bpy.ops.preferences.addon_enable(module=long)
    except Exception as e:
        report_fail(f"Failed to install {addon=} due to {e=}")

    if long not in bpy.context.preferences.addons.keys():
        report_fail(f"Attempted to install {addon=} but wasnt found after install")

    return True
