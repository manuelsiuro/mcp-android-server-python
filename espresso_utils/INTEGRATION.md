# Integration Guide: Espresso Utils

This guide explains how to integrate the Espresso Utils library into your Android project.

## Option 1: Copy Files Directly (Recommended for Generated Tests)

The simplest approach is to copy the utility classes directly into your Android test source set.

### Step 1: Copy Files

Copy the following files to your Android project:

```bash
# From espresso_utils/src/main/kotlin/com/android/test/espresso/utils/
# To your_android_project/app/src/androidTest/kotlin/com/android/test/espresso/utils/

CoordinateConverter.kt
CustomViewActions.kt
EspressoTestHelpers.kt
```

### Step 2: Project Structure

Your Android project structure should look like this:

```
your_android_project/
├── app/
│   └── src/
│       ├── main/
│       │   └── java/com/yourapp/
│       └── androidTest/
│           └── kotlin/
│               ├── com/yourapp/
│               │   └── YourTests.kt
│               └── com/android/test/espresso/utils/
│                   ├── CoordinateConverter.kt
│                   ├── CustomViewActions.kt
│                   └── EspressoTestHelpers.kt
└── build.gradle
```

### Step 3: Verify Dependencies

Ensure your `app/build.gradle` has the required Espresso dependencies:

```gradle
dependencies {
    // Espresso dependencies
    androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
    androidTestImplementation 'androidx.test:runner:1.5.2'
    androidTestImplementation 'androidx.test:rules:1.5.0'
    androidTestImplementation 'androidx.test.ext:junit:1.1.5'

    // Kotlin support
    androidTestImplementation 'org.jetbrains.kotlin:kotlin-stdlib:1.9.0'
}
```

### Step 4: Use in Your Tests

```kotlin
package com.yourapp

import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.android.test.espresso.utils.EspressoTestHelpers.*
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class YourTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testWithCoordinates() {
        // Use the helper methods
        clickAt(100f, 200f)
        clickAtRelative(0.5f, 0.5f)
        clickAtCenter()
    }
}
```

## Option 2: Create a Separate Utility Module (For Multiple Projects)

If you want to reuse the utils across multiple Android projects:

### Step 1: Create Module

Create a new Android library module in your project:

```bash
# In Android Studio: File > New > New Module > Android Library
# Name: espresso-utils
```

### Step 2: Move Files

Move the utility files to the library module:

```
your_android_project/
├── espresso-utils/
│   ├── src/main/kotlin/com/android/test/espresso/utils/
│   │   ├── CoordinateConverter.kt
│   │   ├── CustomViewActions.kt
│   │   └── EspressoTestHelpers.kt
│   └── build.gradle
└── app/
    └── build.gradle
```

### Step 3: Library build.gradle

```gradle
// espresso-utils/build.gradle

plugins {
    id 'com.android.library'
    id 'kotlin-android'
}

android {
    namespace 'com.android.test.espresso.utils'
    compileSdk 34

    defaultConfig {
        minSdk 21
        targetSdk 34
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = '17'
    }
}

dependencies {
    implementation 'androidx.test.espresso:espresso-core:3.5.1'
    implementation 'androidx.test:runner:1.5.2'
    implementation 'org.jetbrains.kotlin:kotlin-stdlib:1.9.0'
}
```

### Step 4: Include Module in App

```gradle
// app/build.gradle

dependencies {
    androidTestImplementation project(':espresso-utils')
    // ... other dependencies
}
```

### Step 5: Settings

```gradle
// settings.gradle

include ':app', ':espresso-utils'
```

## Option 3: Publish as Maven Artifact (For Organization-Wide Use)

For organizations with multiple Android projects:

### Step 1: Configure Publishing

Add to `espresso-utils/build.gradle`:

```gradle
plugins {
    id 'maven-publish'
}

afterEvaluate {
    publishing {
        publications {
            release(MavenPublication) {
                from components.release
                groupId = 'com.yourcompany.test'
                artifactId = 'espresso-utils'
                version = '1.0.0'
            }
        }
        repositories {
            maven {
                url = uri("${project.buildDir}/repo")
            }
        }
    }
}
```

### Step 2: Publish

```bash
./gradlew :espresso-utils:publishReleasePublicationToMavenLocal
```

### Step 3: Use in Projects

```gradle
// In any project's app/build.gradle

repositories {
    mavenLocal()
    // or your company maven repo
}

dependencies {
    androidTestImplementation 'com.yourcompany.test:espresso-utils:1.0.0'
}
```

## Automated Integration for Generated Tests

When tests are generated from recorded scenarios, the code generator automatically:

1. Imports `EspressoTestHelpers` in generated test files
2. Uses `clickAt()`, `clickAtScaled()`, and other helper methods
3. Includes device resolution metadata for scaling

Example generated test:

```kotlin
package com.centile.vera.test

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.android.test.espresso.utils.EspressoTestHelpers
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Generated Espresso test from recorded scenario
 * Recording device: 1080x1920 (xxhdpi)
 */
@RunWith(AndroidJUnit4::class)
class LoginAndSearchContactTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    // Reference device dimensions
    companion object {
        const val REF_WIDTH = 1080
        const val REF_HEIGHT = 1920
    }

    @Test
    fun testScenario() {
        // All coordinate-based clicks automatically scale to current device
        EspressoTestHelpers.clickAt(492f, 562f)

        // Or use scaling explicitly for maximum compatibility
        // EspressoTestHelpers.clickAtScaled(492f, 562f, REF_WIDTH, REF_HEIGHT)
    }
}
```

## Troubleshooting

### Issue: Cannot resolve symbol 'EspressoTestHelpers'

**Solution**: Ensure the files are in the correct package path:
- `androidTest/kotlin/com/android/test/espresso/utils/`

Or verify the module is included in `settings.gradle` if using a separate module.

### Issue: ClassNotFoundException at runtime

**Solution**: Ensure dependencies are in `androidTestImplementation` not just `implementation`:

```gradle
androidTestImplementation 'androidx.test.espresso:espresso-core:3.5.1'
```

### Issue: Coordinates not scaling properly

**Solution**: Print screen info to debug:

```kotlin
@Before
fun setup() {
    EspressoTestHelpers.printScreenInfo()
}
```

### Issue: Tests fail on different devices

**Solution**: Use device-independent coordinates:

```kotlin
// ❌ Device-specific
EspressoTestHelpers.clickAt(540f, 960f)

// ✅ Device-independent
EspressoTestHelpers.clickAtRelative(0.5f, 0.5f)
// or
EspressoTestHelpers.clickAtScaled(540f, 960f, 1080, 1920)
```

## Best Practices

1. **Always include utils in test source set**: Don't add to main source code
2. **Document recording device**: Include device dimensions in test comments
3. **Use relative coordinates when possible**: More resilient than absolute
4. **Test on multiple devices**: Validate scaling works correctly
5. **Keep utils updated**: When updating Android/Espresso versions

## Version Compatibility

| Espresso Utils | Min Android SDK | Espresso Version | Kotlin Version |
|---------------|-----------------|------------------|----------------|
| 1.0.0         | 21 (Lollipop)   | 3.4.0+           | 1.7.0+         |

## Support

For issues or questions:
1. Check the [README.md](README.md) for API documentation
2. Review examples in the main documentation
3. File issues in the project repository
