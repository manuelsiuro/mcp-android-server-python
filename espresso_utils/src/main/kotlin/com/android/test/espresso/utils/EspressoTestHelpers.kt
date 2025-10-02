package com.android.test.espresso.utils

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.ViewInteraction
import androidx.test.espresso.matcher.ViewMatchers.isRoot

/**
 * Helper object providing convenient methods for Espresso tests.
 * Simplifies common test operations with sensible defaults.
 */
object EspressoTestHelpers {

    /**
     * Performs a click at absolute pixel coordinates
     *
     * Usage:
     * ```
     * clickAt(100f, 200f)
     * ```
     */
    @JvmStatic
    fun clickAt(x: Float, y: Float): ViewInteraction {
        return onView(isRoot()).perform(
            CustomViewActions.clickXY(
                x, y,
                CustomViewActions.CoordinateSystem.ABSOLUTE_PIXELS
            )
        )
    }

    /**
     * Performs a click at relative coordinates (0.0-1.0)
     *
     * Usage:
     * ```
     * clickAtRelative(0.5f, 0.3f) // Click at 50% width, 30% height
     * ```
     */
    @JvmStatic
    fun clickAtRelative(relativeX: Float, relativeY: Float): ViewInteraction {
        return onView(isRoot()).perform(
            CustomViewActions.clickXY(
                relativeX, relativeY,
                CustomViewActions.CoordinateSystem.RELATIVE_NORMALIZED
            )
        )
    }

    /**
     * Performs a click at percentage coordinates (0-100)
     *
     * Usage:
     * ```
     * clickAtPercent(50f, 30f) // Click at 50% width, 30% height
     * ```
     */
    @JvmStatic
    fun clickAtPercent(percentX: Float, percentY: Float): ViewInteraction {
        return onView(isRoot()).perform(
            CustomViewActions.clickXY(
                percentX, percentY,
                CustomViewActions.CoordinateSystem.PERCENTAGE
            )
        )
    }

    /**
     * Clicks at the center of the screen
     *
     * Usage:
     * ```
     * clickAtCenter()
     * ```
     */
    @JvmStatic
    fun clickAtCenter(): ViewInteraction {
        return onView(isRoot()).perform(CustomViewActions.clickAtScreenCenter())
    }

    /**
     * Performs a long click at coordinates
     *
     * Usage:
     * ```
     * longClickAt(100f, 200f)
     * longClickAt(100f, 200f, 2000L) // 2 second long click
     * ```
     */
    @JvmStatic
    @JvmOverloads
    fun longClickAt(x: Float, y: Float, durationMs: Long = 1000L): ViewInteraction {
        return onView(isRoot()).perform(
            CustomViewActions.longClickXY(
                x, y,
                CustomViewActions.CoordinateSystem.ABSOLUTE_PIXELS,
                durationMs
            )
        )
    }

    /**
     * Performs a double click at coordinates
     *
     * Usage:
     * ```
     * doubleClickAt(100f, 200f)
     * ```
     */
    @JvmStatic
    fun doubleClickAt(x: Float, y: Float): ViewInteraction {
        return onView(isRoot()).perform(
            CustomViewActions.doubleClickXY(
                x, y,
                CustomViewActions.CoordinateSystem.ABSOLUTE_PIXELS
            )
        )
    }

    /**
     * Performs a swipe from one point to another
     *
     * Usage:
     * ```
     * swipe(100f, 500f, 100f, 200f) // Swipe up
     * swipe(100f, 500f, 100f, 200f, 500L) // Slower swipe
     * ```
     */
    @JvmStatic
    @JvmOverloads
    fun swipe(
        startX: Float,
        startY: Float,
        endX: Float,
        endY: Float,
        durationMs: Long = 300L
    ): ViewInteraction {
        return onView(isRoot()).perform(
            CustomViewActions.swipeXY(
                startX, startY, endX, endY,
                CustomViewActions.CoordinateSystem.ABSOLUTE_PIXELS,
                durationMs
            )
        )
    }

    /**
     * Performs a swipe using relative coordinates
     *
     * Usage:
     * ```
     * swipeRelative(0.5f, 0.8f, 0.5f, 0.2f) // Swipe up from bottom to top, centered
     * ```
     */
    @JvmStatic
    @JvmOverloads
    fun swipeRelative(
        startRelX: Float,
        startRelY: Float,
        endRelX: Float,
        endRelY: Float,
        durationMs: Long = 300L
    ): ViewInteraction {
        return onView(isRoot()).perform(
            CustomViewActions.swipeXY(
                startRelX, startRelY, endRelX, endRelY,
                CustomViewActions.CoordinateSystem.RELATIVE_NORMALIZED,
                durationMs
            )
        )
    }

    /**
     * Clicks at scaled coordinates from a reference device
     *
     * Usage:
     * ```
     * // Recorded on 1080x1920 device, replay on any device
     * clickAtScaled(540f, 960f, 1080, 1920)
     * ```
     */
    @JvmStatic
    fun clickAtScaled(
        x: Float,
        y: Float,
        referenceWidth: Int,
        referenceHeight: Int
    ): ViewInteraction {
        return onView(isRoot()).perform(
            CustomViewActions.clickAtScaled(x, y, referenceWidth, referenceHeight)
        )
    }

    /**
     * Gets screen information (useful for debugging)
     *
     * Usage:
     * ```
     * println(getScreenInfo())
     * ```
     */
    @JvmStatic
    fun getScreenInfo(): String {
        return CoordinateConverter.getScreenInfo()
    }

    /**
     * Logs screen information to console
     */
    @JvmStatic
    fun printScreenInfo() {
        println(CoordinateConverter.getScreenInfo())
    }
}
