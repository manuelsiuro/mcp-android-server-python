package com.centile.vera.test

import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.matcher.ViewMatchers.isRoot
import androidx.test.espresso.matcher.ViewMatchers.withId
import androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.android.test.espresso.utils.EspressoTestHelpers
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Generated Espresso test from recorded scenario
 * Scenario: login_and_search_contact_20251002_143027
 * Generated on: 2025-10-02T14:30:27.283688
 *
 * Recording device: 1080x1920 (xxhdpi)
 *
 * This test demonstrates the new screen-resolution-aware coordinate system.
 * All coordinate-based actions automatically work on any device size!
 */
@RunWith(AndroidJUnit4::class)
class LoginAndSearchContactTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    // Reference device dimensions (device used for recording)
    companion object {
        const val REF_WIDTH = 1080
        const val REF_HEIGHT = 1920
    }

    @Before
    fun setup() {
        // Optional: Print screen info for debugging
        // EspressoTestHelpers.printScreenInfo()
    }

    @Test
    fun testScenario() {
        // Generated from scenario: login_and_search_contact_20251002_143027
        // Created: 2025-10-02T14:30:27.283688

        // Action 1: start_app
        // TODO: Implement start_app action manually
        Thread.sleep(1000L)

        // Action 2: click - Username field
        Thread.sleep(24885L)
        onView(withId(R.id.text_input_layout_username)).perform(click())
        Thread.sleep(1000L)

        // Action 3: send_text - Enter username
        Thread.sleep(7774L)
        onView(withId(R.id.text_input_layout_username)).perform(clearText(), typeText("msiuro"))
        Thread.sleep(1000L)

        // Action 4: click - Password field
        Thread.sleep(4111L)
        onView(withId(R.id.text_input_layout_password)).perform(click())
        Thread.sleep(1000L)

        // Action 5: send_text - Enter password
        Thread.sleep(4414L)
        onView(withId(R.id.text_input_layout_password)).perform(clearText(), typeText("281281"))
        Thread.sleep(1000L)

        // Action 6: click - Login button
        Thread.sleep(4126L)
        onView(withId(R.id.login_button)).perform(click())
        Thread.sleep(1000L)

        // Action 7: click - Contacts tab
        Thread.sleep(26756L)
        onView(withId(R.id.layout_contact)).perform(click())
        Thread.sleep(1000L)

        // Action 8: click_at - Search field (RESOLUTION-AWARE!)
        // This click works on ANY device - coordinates automatically scale!
        Thread.sleep(19523L)
        EspressoTestHelpers.clickAt(492.0f, 562.0f)
        Thread.sleep(1000L)

        // Alternative approach with explicit scaling (maximum compatibility):
        // EspressoTestHelpers.clickAtScaled(492.0f, 562.0f, REF_WIDTH, REF_HEIGHT)

        // Alternative approach with relative coordinates:
        // EspressoTestHelpers.clickAtRelative(0.456f, 0.293f)  // 492/1080, 562/1920

        // Action 9: send_text - Search query
        Thread.sleep(4460L)
        onView(withText("Search from contacts")).perform(typeText("catz"))
        Thread.sleep(1000L)

        // Action 10: click_xpath - Contact result
        Thread.sleep(21574L)
        onView(withText("Jean-François CATZ")).perform(click())
        Thread.sleep(1000L)
    }

    /**
     * Example test showing different coordinate approaches
     */
    @Test
    fun testCoordinateVariants() {
        // Method 1: Absolute pixels (simplest, but device-specific)
        EspressoTestHelpers.clickAt(100f, 200f)

        // Method 2: Relative coordinates (device-independent, 0.0-1.0)
        EspressoTestHelpers.clickAtRelative(0.5f, 0.5f)  // Center of screen

        // Method 3: Percentage (device-independent, 0-100)
        EspressoTestHelpers.clickAtPercent(50f, 50f)  // Center of screen

        // Method 4: Scaled from reference device (best for recorded tests)
        EspressoTestHelpers.clickAtScaled(540f, 960f, 1080, 1920)

        // Method 5: Convenience methods
        EspressoTestHelpers.clickAtCenter()  // Click center
        EspressoTestHelpers.longClickAt(100f, 200f, 2000L)  // Long press 2 seconds
        EspressoTestHelpers.doubleClickAt(100f, 200f)  // Double click
        EspressoTestHelpers.swipe(100f, 500f, 100f, 200f)  // Swipe up
    }

    /**
     * Example showing relative swipe (works on any device)
     */
    @Test
    fun testDeviceIndependentSwipe() {
        // Swipe from 80% down to 20% down (centered horizontally)
        // This works identically on phones, tablets, any resolution!
        EspressoTestHelpers.swipeRelative(
            startRelX = 0.5f,  // Center horizontally
            startRelY = 0.8f,  // 80% from top
            endRelX = 0.5f,    // Still centered
            endRelY = 0.2f     // 20% from top
        )
    }
}
