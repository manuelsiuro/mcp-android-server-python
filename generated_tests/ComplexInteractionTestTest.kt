package com.example.test

androidx.test.espresso.Espresso.pressKey
androidx.test.espresso.action.ViewActions.click
androidx.test.espresso.action.ViewActions.longClick
androidx.test.espresso.action.ViewActions.swipe
androidx.test.espresso.action.ViewActions.swipeUp
androidx.test.espresso.matcher.ViewMatchers.withText
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.*
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * Generated Espresso test from recorded scenario
 * Scenario: complex_interaction_test
 * Generated on: 2025-01-01T10:00:00Z
 *
 * Original scenario file: Unknown
 */
@RunWith(AndroidJUnit4::class)
class ComplexInteractionTestTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testScenario() {
        // Generated from scenario: complex_interaction_test
        // Created: 2025-01-01T10:00:00Z
        
        // Action 1: click_at
        perform(clickXY(540, 1200))

        // Action 2: long_click
        onView(withText("Item")).perform(longClick())

        // Action 3: swipe
        perform(swipe(500, 1500, 500, 500))

        // Action 4: scroll_forward
        perform(swipeUp())

        // Action 5: press_key
        pressKey("back")

    }
}
