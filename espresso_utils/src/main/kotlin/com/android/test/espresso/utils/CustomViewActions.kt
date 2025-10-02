package com.android.test.espresso.utils

import android.view.InputDevice
import android.view.MotionEvent
import android.view.View
import androidx.test.espresso.PerformException
import androidx.test.espresso.UiController
import androidx.test.espresso.ViewAction
import androidx.test.espresso.action.GeneralClickAction
import androidx.test.espresso.action.Press
import androidx.test.espresso.action.Tap
import androidx.test.espresso.matcher.ViewMatchers
import androidx.test.espresso.util.HumanReadables
import org.hamcrest.Matcher

/**
 * Custom ViewActions for Espresso tests that provide advanced interaction capabilities.
 */
object CustomViewActions {

    /**
     * Coordinate system enum for specifying how coordinates should be interpreted
     */
    enum class CoordinateSystem {
        ABSOLUTE_PIXELS,    // Raw pixel coordinates
        RELATIVE_NORMALIZED, // 0.0 to 1.0 (percentage of screen)
        PERCENTAGE          // 0 to 100 (percentage of screen)
    }

    /**
     * Creates a ViewAction that clicks at specific coordinates on the root view.
     * This is the main entry point for coordinate-based clicking.
     *
     * @param x X coordinate
     * @param y Y coordinate
     * @param coordinateSystem How to interpret the coordinates (default: ABSOLUTE_PIXELS)
     * @return ViewAction that performs the click
     *
     * Example usage:
     * ```
     * // Absolute coordinates
     * onView(isRoot()).perform(clickXY(100f, 200f))
     *
     * // Relative coordinates (50% of screen width, 30% of screen height)
     * onView(isRoot()).perform(clickXY(0.5f, 0.3f, CoordinateSystem.RELATIVE_NORMALIZED))
     *
     * // Percentage coordinates
     * onView(isRoot()).perform(clickXY(50f, 30f, CoordinateSystem.PERCENTAGE))
     * ```
     */
    @JvmStatic
    @JvmOverloads
    fun clickXY(
        x: Float,
        y: Float,
        coordinateSystem: CoordinateSystem = CoordinateSystem.ABSOLUTE_PIXELS
    ): ViewAction {
        return object : ViewAction {
            override fun getConstraints(): Matcher<View> {
                return ViewMatchers.isRoot()
            }

            override fun getDescription(): String {
                return "Click at coordinates ($x, $y) using $coordinateSystem"
            }

            override fun perform(uiController: UiController, view: View) {
                // Convert coordinates to absolute pixels if needed
                val (absoluteX, absoluteY) = when (coordinateSystem) {
                    CoordinateSystem.ABSOLUTE_PIXELS -> Pair(x, y)
                    CoordinateSystem.RELATIVE_NORMALIZED ->
                        CoordinateConverter.relativeToAbsolute(x, y)
                    CoordinateSystem.PERCENTAGE ->
                        CoordinateConverter.percentageToAbsolute(x, y)
                }

                // Validate coordinates are within bounds
                if (!CoordinateConverter.isWithinBounds(absoluteX, absoluteY)) {
                    throw PerformException.Builder()
                        .withActionDescription(description)
                        .withViewDescription(HumanReadables.describe(view))
                        .withCause(
                            IllegalArgumentException(
                                "Coordinates ($absoluteX, $absoluteY) are outside screen bounds. " +
                                CoordinateConverter.getScreenInfo()
                            )
                        )
                        .build()
                }

                // Get screen coordinates (view coordinates to screen coordinates)
                val screenPos = IntArray(2)
                view.getLocationOnScreen(screenPos)

                // Perform the click
                val downTime = System.currentTimeMillis()
                val eventTime = System.currentTimeMillis()

                // Create and dispatch DOWN event
                val down = MotionEvent.obtain(
                    downTime,
                    eventTime,
                    MotionEvent.ACTION_DOWN,
                    absoluteX,
                    absoluteY,
                    0
                ).apply {
                    source = InputDevice.SOURCE_TOUCHSCREEN
                }

                if (!view.dispatchTouchEvent(down)) {
                    down.recycle()
                    throw PerformException.Builder()
                        .withActionDescription(description)
                        .withViewDescription(HumanReadables.describe(view))
                        .withCause(RuntimeException("Failed to dispatch DOWN event"))
                        .build()
                }

                uiController.loopMainThreadForAtLeast(10)

                // Create and dispatch UP event
                val up = MotionEvent.obtain(
                    downTime,
                    eventTime + 100,
                    MotionEvent.ACTION_UP,
                    absoluteX,
                    absoluteY,
                    0
                ).apply {
                    source = InputDevice.SOURCE_TOUCHSCREEN
                }

                if (!view.dispatchTouchEvent(up)) {
                    up.recycle()
                    down.recycle()
                    throw PerformException.Builder()
                        .withActionDescription(description)
                        .withViewDescription(HumanReadables.describe(view))
                        .withCause(RuntimeException("Failed to dispatch UP event"))
                        .build()
                }

                // Recycle events
                down.recycle()
                up.recycle()

                // Wait for UI to settle
                uiController.loopMainThreadForAtLeast(100)
            }
        }
    }

    /**
     * Clicks at absolute pixel coordinates (shorthand for clickXY with ABSOLUTE_PIXELS)
     */
    @JvmStatic
    fun clickAtPixels(x: Float, y: Float): ViewAction {
        return clickXY(x, y, CoordinateSystem.ABSOLUTE_PIXELS)
    }

    /**
     * Clicks at relative coordinates (0.0 to 1.0)
     */
    @JvmStatic
    fun clickAtRelative(relativeX: Float, relativeY: Float): ViewAction {
        return clickXY(relativeX, relativeY, CoordinateSystem.RELATIVE_NORMALIZED)
    }

    /**
     * Clicks at percentage coordinates (0 to 100)
     */
    @JvmStatic
    fun clickAtPercentage(percentX: Float, percentY: Float): ViewAction {
        return clickXY(percentX, percentY, CoordinateSystem.PERCENTAGE)
    }

    /**
     * Clicks at the center of the screen
     */
    @JvmStatic
    fun clickAtScreenCenter(): ViewAction {
        return clickXY(0.5f, 0.5f, CoordinateSystem.RELATIVE_NORMALIZED)
    }

    /**
     * Clicks at scaled coordinates from a reference device.
     * Useful for replaying recorded tests on different devices.
     *
     * @param x Original X coordinate
     * @param y Original Y coordinate
     * @param referenceWidth Width of the device where coordinates were recorded
     * @param referenceHeight Height of the device where coordinates were recorded
     */
    @JvmStatic
    fun clickAtScaled(
        x: Float,
        y: Float,
        referenceWidth: Int,
        referenceHeight: Int
    ): ViewAction {
        val (scaledX, scaledY) = CoordinateConverter.scaleCoordinates(
            x, y, referenceWidth, referenceHeight
        )
        return clickXY(scaledX, scaledY, CoordinateSystem.ABSOLUTE_PIXELS)
    }

    /**
     * Long click at specific coordinates
     */
    @JvmStatic
    @JvmOverloads
    fun longClickXY(
        x: Float,
        y: Float,
        coordinateSystem: CoordinateSystem = CoordinateSystem.ABSOLUTE_PIXELS,
        durationMs: Long = 1000L
    ): ViewAction {
        return object : ViewAction {
            override fun getConstraints(): Matcher<View> {
                return ViewMatchers.isRoot()
            }

            override fun getDescription(): String {
                return "Long click at coordinates ($x, $y) for ${durationMs}ms using $coordinateSystem"
            }

            override fun perform(uiController: UiController, view: View) {
                val (absoluteX, absoluteY) = when (coordinateSystem) {
                    CoordinateSystem.ABSOLUTE_PIXELS -> Pair(x, y)
                    CoordinateSystem.RELATIVE_NORMALIZED ->
                        CoordinateConverter.relativeToAbsolute(x, y)
                    CoordinateSystem.PERCENTAGE ->
                        CoordinateConverter.percentageToAbsolute(x, y)
                }

                if (!CoordinateConverter.isWithinBounds(absoluteX, absoluteY)) {
                    throw PerformException.Builder()
                        .withActionDescription(description)
                        .withViewDescription(HumanReadables.describe(view))
                        .withCause(
                            IllegalArgumentException(
                                "Coordinates ($absoluteX, $absoluteY) are outside screen bounds"
                            )
                        )
                        .build()
                }

                val downTime = System.currentTimeMillis()

                // DOWN event
                val down = MotionEvent.obtain(
                    downTime,
                    downTime,
                    MotionEvent.ACTION_DOWN,
                    absoluteX,
                    absoluteY,
                    0
                ).apply { source = InputDevice.SOURCE_TOUCHSCREEN }

                view.dispatchTouchEvent(down)

                // Hold for specified duration
                uiController.loopMainThreadForAtLeast(durationMs)

                // UP event
                val up = MotionEvent.obtain(
                    downTime,
                    downTime + durationMs,
                    MotionEvent.ACTION_UP,
                    absoluteX,
                    absoluteY,
                    0
                ).apply { source = InputDevice.SOURCE_TOUCHSCREEN }

                view.dispatchTouchEvent(up)

                down.recycle()
                up.recycle()

                uiController.loopMainThreadForAtLeast(100)
            }
        }
    }

    /**
     * Double click at specific coordinates
     */
    @JvmStatic
    @JvmOverloads
    fun doubleClickXY(
        x: Float,
        y: Float,
        coordinateSystem: CoordinateSystem = CoordinateSystem.ABSOLUTE_PIXELS
    ): ViewAction {
        return object : ViewAction {
            override fun getConstraints(): Matcher<View> {
                return ViewMatchers.isRoot()
            }

            override fun getDescription(): String {
                return "Double click at coordinates ($x, $y) using $coordinateSystem"
            }

            override fun perform(uiController: UiController, view: View) {
                // Perform first click
                clickXY(x, y, coordinateSystem).perform(uiController, view)

                // Small delay between clicks
                uiController.loopMainThreadForAtLeast(100)

                // Perform second click
                clickXY(x, y, coordinateSystem).perform(uiController, view)
            }
        }
    }

    /**
     * Swipe from one coordinate to another
     */
    @JvmStatic
    @JvmOverloads
    fun swipeXY(
        startX: Float,
        startY: Float,
        endX: Float,
        endY: Float,
        coordinateSystem: CoordinateSystem = CoordinateSystem.ABSOLUTE_PIXELS,
        durationMs: Long = 300L
    ): ViewAction {
        return object : ViewAction {
            override fun getConstraints(): Matcher<View> {
                return ViewMatchers.isRoot()
            }

            override fun getDescription(): String {
                return "Swipe from ($startX, $startY) to ($endX, $endY) using $coordinateSystem"
            }

            override fun perform(uiController: UiController, view: View) {
                val (absStartX, absStartY) = when (coordinateSystem) {
                    CoordinateSystem.ABSOLUTE_PIXELS -> Pair(startX, startY)
                    CoordinateSystem.RELATIVE_NORMALIZED ->
                        CoordinateConverter.relativeToAbsolute(startX, startY)
                    CoordinateSystem.PERCENTAGE ->
                        CoordinateConverter.percentageToAbsolute(startX, startY)
                }

                val (absEndX, absEndY) = when (coordinateSystem) {
                    CoordinateSystem.ABSOLUTE_PIXELS -> Pair(endX, endY)
                    CoordinateSystem.RELATIVE_NORMALIZED ->
                        CoordinateConverter.relativeToAbsolute(endX, endY)
                    CoordinateSystem.PERCENTAGE ->
                        CoordinateConverter.percentageToAbsolute(endX, endY)
                }

                val downTime = System.currentTimeMillis()
                val steps = 20 // Number of intermediate points for smooth swipe

                // DOWN event at start position
                val down = MotionEvent.obtain(
                    downTime,
                    downTime,
                    MotionEvent.ACTION_DOWN,
                    absStartX,
                    absStartY,
                    0
                ).apply { source = InputDevice.SOURCE_TOUCHSCREEN }

                view.dispatchTouchEvent(down)
                down.recycle()

                // MOVE events
                val stepDuration = durationMs / steps
                for (i in 1..steps) {
                    val progress = i.toFloat() / steps
                    val currentX = absStartX + (absEndX - absStartX) * progress
                    val currentY = absStartY + (absEndY - absStartY) * progress

                    val move = MotionEvent.obtain(
                        downTime,
                        downTime + (i * stepDuration),
                        MotionEvent.ACTION_MOVE,
                        currentX,
                        currentY,
                        0
                    ).apply { source = InputDevice.SOURCE_TOUCHSCREEN }

                    view.dispatchTouchEvent(move)
                    move.recycle()

                    uiController.loopMainThreadForAtLeast(stepDuration)
                }

                // UP event at end position
                val up = MotionEvent.obtain(
                    downTime,
                    downTime + durationMs,
                    MotionEvent.ACTION_UP,
                    absEndX,
                    absEndY,
                    0
                ).apply { source = InputDevice.SOURCE_TOUCHSCREEN }

                view.dispatchTouchEvent(up)
                up.recycle()

                uiController.loopMainThreadForAtLeast(100)
            }
        }
    }
}
