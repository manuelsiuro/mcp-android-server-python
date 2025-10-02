package com.android.test.espresso.utils

import android.content.Context
import android.graphics.Point
import android.util.DisplayMetrics
import android.view.WindowManager
import androidx.test.platform.app.InstrumentationRegistry

/**
 * Utility class for converting between different coordinate systems.
 * Handles screen resolution differences across devices by supporting:
 * - Absolute coordinates (pixels)
 * - Relative coordinates (0.0 to 1.0)
 * - Percentage coordinates (0 to 100)
 */
object CoordinateConverter {

    /**
     * Data class representing a point with different coordinate representations
     */
    data class ScreenPoint(
        val absoluteX: Float,
        val absoluteY: Float,
        val relativeX: Float,
        val relativeY: Float
    )

    /**
     * Gets the screen dimensions of the current device
     */
    fun getScreenDimensions(): Point {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
        val display = windowManager.defaultDisplay
        val size = Point()
        display.getRealSize(size)
        return size
    }

    /**
     * Gets display metrics for the current device
     */
    fun getDisplayMetrics(): DisplayMetrics {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val windowManager = context.getSystemService(Context.WINDOW_SERVICE) as WindowManager
        val metrics = DisplayMetrics()
        windowManager.defaultDisplay.getMetrics(metrics)
        return metrics
    }

    /**
     * Converts absolute coordinates (pixels) to relative coordinates (0.0-1.0)
     */
    fun absoluteToRelative(absoluteX: Float, absoluteY: Float): Pair<Float, Float> {
        val screenSize = getScreenDimensions()
        val relativeX = absoluteX / screenSize.x
        val relativeY = absoluteY / screenSize.y
        return Pair(relativeX, relativeY)
    }

    /**
     * Converts relative coordinates (0.0-1.0) to absolute coordinates (pixels)
     */
    fun relativeToAbsolute(relativeX: Float, relativeY: Float): Pair<Float, Float> {
        val screenSize = getScreenDimensions()
        val absoluteX = relativeX * screenSize.x
        val absoluteY = relativeY * screenSize.y
        return Pair(absoluteX, absoluteY)
    }

    /**
     * Converts percentage coordinates (0-100) to absolute coordinates (pixels)
     */
    fun percentageToAbsolute(percentX: Float, percentY: Float): Pair<Float, Float> {
        val relativeX = percentX / 100f
        val relativeY = percentY / 100f
        return relativeToAbsolute(relativeX, relativeY)
    }

    /**
     * Converts absolute coordinates to percentage (0-100)
     */
    fun absoluteToPercentage(absoluteX: Float, absoluteY: Float): Pair<Float, Float> {
        val (relativeX, relativeY) = absoluteToRelative(absoluteX, absoluteY)
        return Pair(relativeX * 100f, relativeY * 100f)
    }

    /**
     * Creates a ScreenPoint with all coordinate representations
     */
    fun createScreenPoint(absoluteX: Float, absoluteY: Float): ScreenPoint {
        val (relativeX, relativeY) = absoluteToRelative(absoluteX, absoluteY)
        return ScreenPoint(absoluteX, absoluteY, relativeX, relativeY)
    }

    /**
     * Creates a ScreenPoint from relative coordinates
     */
    fun createScreenPointFromRelative(relativeX: Float, relativeY: Float): ScreenPoint {
        val (absoluteX, absoluteY) = relativeToAbsolute(relativeX, relativeY)
        return ScreenPoint(absoluteX, absoluteY, relativeX, relativeY)
    }

    /**
     * Scales coordinates from a reference device to the current device
     * Useful when coordinates were recorded on one device and need to be replayed on another
     *
     * @param x Original X coordinate
     * @param y Original Y coordinate
     * @param referenceWidth Width of the reference device
     * @param referenceHeight Height of the reference device
     * @return Scaled coordinates for the current device
     */
    fun scaleCoordinates(
        x: Float,
        y: Float,
        referenceWidth: Int,
        referenceHeight: Int
    ): Pair<Float, Float> {
        val currentSize = getScreenDimensions()
        val scaleX = currentSize.x.toFloat() / referenceWidth
        val scaleY = currentSize.y.toFloat() / referenceHeight
        return Pair(x * scaleX, y * scaleY)
    }

    /**
     * Gets the density-independent pixel (dp) to pixel conversion factor
     */
    fun getDensity(): Float {
        return getDisplayMetrics().density
    }

    /**
     * Converts dp to pixels
     */
    fun dpToPx(dp: Float): Float {
        return dp * getDensity()
    }

    /**
     * Converts pixels to dp
     */
    fun pxToDp(px: Float): Float {
        return px / getDensity()
    }

    /**
     * Checks if coordinates are within screen bounds
     */
    fun isWithinBounds(x: Float, y: Float): Boolean {
        val screenSize = getScreenDimensions()
        return x >= 0 && x <= screenSize.x && y >= 0 && y <= screenSize.y
    }

    /**
     * Clamps coordinates to screen bounds
     */
    fun clampToBounds(x: Float, y: Float): Pair<Float, Float> {
        val screenSize = getScreenDimensions()
        val clampedX = x.coerceIn(0f, screenSize.x.toFloat())
        val clampedY = y.coerceIn(0f, screenSize.y.toFloat())
        return Pair(clampedX, clampedY)
    }

    /**
     * Gets screen information as a formatted string (useful for debugging)
     */
    fun getScreenInfo(): String {
        val size = getScreenDimensions()
        val metrics = getDisplayMetrics()
        return """
            Screen Information:
            - Resolution: ${size.x}x${size.y} pixels
            - Density: ${metrics.density} (${metrics.densityDpi} dpi)
            - Density bucket: ${getDensityBucket(metrics.densityDpi)}
            - Scaled Density: ${metrics.scaledDensity}
        """.trimIndent()
    }

    private fun getDensityBucket(dpi: Int): String {
        return when {
            dpi <= 120 -> "ldpi"
            dpi <= 160 -> "mdpi"
            dpi <= 240 -> "hdpi"
            dpi <= 320 -> "xhdpi"
            dpi <= 480 -> "xxhdpi"
            dpi <= 640 -> "xxxhdpi"
            else -> "unknown"
        }
    }
}
