# Espresso Utils - Screen-Resolution-Aware Testing

A comprehensive utility library for Espresso tests that provides coordinate-based interactions with automatic screen resolution handling. This library ensures your tests work consistently across devices with different screen sizes and resolutions.

## Features

✅ **Multi-Resolution Support**: Automatic coordinate scaling for different screen sizes
✅ **Multiple Coordinate Systems**: Absolute pixels, relative (0.0-1.0), and percentage (0-100)
✅ **Rich API**: Click, long click, double click, and swipe actions
✅ **Safe Execution**: Automatic bounds checking and error handling
✅ **Easy Integration**: Simple helper methods for common operations
✅ **Debug Support**: Screen information utilities for troubleshooting

## Quick Start

### 1. Add to Your Test Class

```kotlin
import com.android.test.espresso.utils.EspressoTestHelpers.*
import com.android.test.espresso.utils.CustomViewActions

@RunWith(AndroidJUnit4::class)
class MyTest {
    @Test
    fun testClickAtCoordinates() {
        // Click at absolute pixel coordinates
        clickAt(100f, 200f)

        // Click at 50% width, 30% height (works on any device!)
        clickAtRelative(0.5f, 0.3f)

        // Click at center
        clickAtCenter()
    }
}
```

## Usage Examples

### Basic Clicking

```kotlin
// Absolute pixel coordinates
clickAt(540f, 960f)

// Relative coordinates (50% of screen width, 50% of screen height)
clickAtRelative(0.5f, 0.5f)

// Percentage coordinates
clickAtPercent(50f, 50f)

// Center of screen
clickAtCenter()
```

### Advanced Interactions

```kotlin
// Long click (default 1 second)
longClickAt(100f, 200f)

// Long click with custom duration
longClickAt(100f, 200f, 2000L) // 2 seconds

// Double click
doubleClickAt(100f, 200f)

// Swipe gesture
swipe(100f, 500f, 100f, 200f) // Swipe up

// Swipe with custom duration
swipe(100f, 500f, 100f, 200f, 500L) // Slower swipe

// Relative swipe (works on any screen size)
swipeRelative(0.5f, 0.8f, 0.5f, 0.2f) // Swipe up, centered
```

### Cross-Device Testing

One of the most powerful features is the ability to record tests on one device and replay them on another:

```kotlin
// Coordinates were recorded on a 1080x1920 device
// This automatically scales them for the current device
clickAtScaled(540f, 960f, 1080, 1920)

// Now the test works correctly on:
// - Small phones (e.g., 720x1280)
// - Large phones (e.g., 1440x2560)
// - Tablets (e.g., 1600x2560)
```

### Using Custom ViewActions Directly

For more control, use the `CustomViewActions` class directly:

```kotlin
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.matcher.ViewMatchers.isRoot
import com.android.test.espresso.utils.CustomViewActions
import com.android.test.espresso.utils.CustomViewActions.CoordinateSystem

@Test
fun testWithCustomActions() {
    // Click with explicit coordinate system
    onView(isRoot()).perform(
        CustomViewActions.clickXY(
            100f, 200f,
            CoordinateSystem.ABSOLUTE_PIXELS
        )
    )

    // Relative click
    onView(isRoot()).perform(
        CustomViewActions.clickXY(
            0.5f, 0.3f,
            CoordinateSystem.RELATIVE_NORMALIZED
        )
    )

    // Percentage click
    onView(isRoot()).perform(
        CustomViewActions.clickXY(
            50f, 30f,
            CoordinateSystem.PERCENTAGE
        )
    )
}
```

## Coordinate Systems

### 1. Absolute Pixels (`ABSOLUTE_PIXELS`)

Raw pixel coordinates. Use this when you know the exact pixel position.

```kotlin
clickAt(100f, 200f) // Click at x=100px, y=200px
```

**Pros**: Precise, simple
**Cons**: Device-specific, won't work on different screen sizes

### 2. Relative Normalized (`RELATIVE_NORMALIZED`)

Coordinates from 0.0 to 1.0 representing percentage of screen dimensions.

```kotlin
clickAtRelative(0.5f, 0.5f) // Click at center (50% width, 50% height)
clickAtRelative(0.25f, 0.75f) // Click at 25% from left, 75% from top
```

**Pros**: Device-independent, intuitive for proportional positions
**Cons**: Requires decimal values

### 3. Percentage (`PERCENTAGE`)

Coordinates from 0 to 100 representing percentage of screen dimensions.

```kotlin
clickAtPercent(50f, 50f) // Click at center
clickAtPercent(25f, 75f) // Click at 25% from left, 75% from top
```

**Pros**: Device-independent, easy to understand
**Cons**: None really - same as relative but with whole numbers

## Resolution Handling

The library automatically handles different screen resolutions through the `CoordinateConverter` class:

```kotlin
// Get current screen dimensions
val screenSize = CoordinateConverter.getScreenDimensions()
println("Screen: ${screenSize.x}x${screenSize.y}")

// Convert between coordinate systems
val (absX, absY) = CoordinateConverter.relativeToAbsolute(0.5f, 0.5f)
val (relX, relY) = CoordinateConverter.absoluteToRelative(540f, 960f)

// Scale coordinates from one device to another
val (scaledX, scaledY) = CoordinateConverter.scaleCoordinates(
    x = 540f,
    y = 960f,
    referenceWidth = 1080,
    referenceHeight = 1920
)

// Check if coordinates are valid
val isValid = CoordinateConverter.isWithinBounds(100f, 200f)

// Clamp coordinates to screen bounds
val (clampedX, clampedY) = CoordinateConverter.clampToBounds(5000f, 5000f)
```

## Debugging & Troubleshooting

### Print Screen Information

```kotlin
@Test
fun debugScreenInfo() {
    printScreenInfo()
    // Output:
    // Screen Information:
    // - Resolution: 1080x1920 pixels
    // - Density: 3.0 (480 dpi)
    // - Density bucket: xxhdpi
    // - Scaled Density: 3.0
}
```

### Validate Coordinates Before Clicking

```kotlin
val x = 100f
val y = 200f

if (CoordinateConverter.isWithinBounds(x, y)) {
    clickAt(x, y)
} else {
    println("Coordinates out of bounds!")
    println(getScreenInfo())
}
```

### Handle Failed Clicks

```kotlin
try {
    clickAt(10000f, 10000f) // Out of bounds
} catch (e: PerformException) {
    // Exception will include screen information
    println("Click failed: ${e.message}")
}
```

## Integration with Generated Tests

When tests are generated from recorded scenarios, they should use the scaled coordinate approach:

```kotlin
@Test
fun generatedTest() {
    // Original recording device: 1080x1920
    val REF_WIDTH = 1080
    val REF_HEIGHT = 1920

    // Recorded coordinates are automatically scaled
    clickAtScaled(540f, 960f, REF_WIDTH, REF_HEIGHT)
    clickAtScaled(300f, 500f, REF_WIDTH, REF_HEIGHT)

    // This works on ANY device!
}
```

## Best Practices

### 1. Use Relative Coordinates for UI Elements

```kotlin
// ❌ Bad - Device specific
clickAt(540f, 960f)

// ✅ Good - Works on all devices
clickAtRelative(0.5f, 0.5f)
```

### 2. Record Reference Resolution for Absolute Coordinates

```kotlin
// ❌ Bad - Will break on different devices
clickAt(492f, 562f)

// ✅ Good - Scales to any device
clickAtScaled(492f, 562f, 1080, 1920)
```

### 3. Use Helper Methods for Common Operations

```kotlin
// ❌ More verbose
onView(isRoot()).perform(
    CustomViewActions.clickXY(0.5f, 0.5f, CoordinateSystem.RELATIVE_NORMALIZED)
)

// ✅ Cleaner
clickAtRelative(0.5f, 0.5f)
```

### 4. Debug with Screen Info

```kotlin
@Before
fun setup() {
    // Print screen info before each test
    printScreenInfo()
}
```

## API Reference

### EspressoTestHelpers

| Method | Description |
|--------|-------------|
| `clickAt(x, y)` | Click at absolute pixel coordinates |
| `clickAtRelative(relX, relY)` | Click at relative coordinates (0.0-1.0) |
| `clickAtPercent(percX, percY)` | Click at percentage coordinates (0-100) |
| `clickAtCenter()` | Click at screen center |
| `clickAtScaled(x, y, refW, refH)` | Click at scaled coordinates from reference device |
| `longClickAt(x, y, duration?)` | Long click at coordinates |
| `doubleClickAt(x, y)` | Double click at coordinates |
| `swipe(x1, y1, x2, y2, duration?)` | Swipe from one point to another |
| `swipeRelative(...)` | Swipe using relative coordinates |
| `getScreenInfo()` | Get screen information string |
| `printScreenInfo()` | Print screen information to console |

### CustomViewActions

| Method | Description |
|--------|-------------|
| `clickXY(x, y, coordSystem?)` | Main click action with coordinate system |
| `longClickXY(x, y, coordSystem?, duration?)` | Long click action |
| `doubleClickXY(x, y, coordSystem?)` | Double click action |
| `swipeXY(x1, y1, x2, y2, coordSystem?, duration?)` | Swipe action |
| `clickAtPixels(x, y)` | Shorthand for absolute pixel click |
| `clickAtRelative(relX, relY)` | Shorthand for relative click |
| `clickAtPercentage(percX, percY)` | Shorthand for percentage click |
| `clickAtScreenCenter()` | Click at screen center |
| `clickAtScaled(x, y, refW, refH)` | Click at scaled coordinates |

### CoordinateConverter

| Method | Description |
|--------|-------------|
| `getScreenDimensions()` | Get screen width and height |
| `getDisplayMetrics()` | Get display metrics |
| `absoluteToRelative(x, y)` | Convert absolute to relative coordinates |
| `relativeToAbsolute(relX, relY)` | Convert relative to absolute coordinates |
| `percentageToAbsolute(percX, percY)` | Convert percentage to absolute |
| `absoluteToPercentage(x, y)` | Convert absolute to percentage |
| `scaleCoordinates(x, y, refW, refH)` | Scale from reference device |
| `isWithinBounds(x, y)` | Check if coordinates are valid |
| `clampToBounds(x, y)` | Clamp coordinates to screen |
| `getScreenInfo()` | Get formatted screen information |
| `getDensity()` | Get screen density |
| `dpToPx(dp)` | Convert DP to pixels |
| `pxToDp(px)` | Convert pixels to DP |

## Common Issues & Solutions

### Issue: Clicks not registering

**Solution**: Ensure you're clicking on the root view:

```kotlin
onView(isRoot()).perform(CustomViewActions.clickXY(...))
// OR use helpers which do this automatically:
clickAt(100f, 200f)
```

### Issue: Coordinates out of bounds

**Solution**: Use relative coordinates or validate bounds:

```kotlin
// Option 1: Use relative coordinates
clickAtRelative(0.5f, 0.3f)

// Option 2: Validate before clicking
if (CoordinateConverter.isWithinBounds(x, y)) {
    clickAt(x, y)
}

// Option 3: Use clamping
val (safeX, safeY) = CoordinateConverter.clampToBounds(x, y)
clickAt(safeX, safeY)
```

### Issue: Test works on one device but fails on another

**Solution**: Use device-independent coordinates:

```kotlin
// ❌ Device-specific
clickAt(540f, 960f)

// ✅ Device-independent options:

// Option 1: Relative
clickAtRelative(0.5f, 0.5f)

// Option 2: Percentage
clickAtPercent(50f, 50f)

// Option 3: Scaled from reference
clickAtScaled(540f, 960f, 1080, 1920)
```

## License

Part of the MCP Android Server project.

## Contributing

When adding new coordinate-based actions, ensure they:
1. Support all three coordinate systems
2. Include bounds checking
3. Handle errors gracefully
4. Include documentation and examples
