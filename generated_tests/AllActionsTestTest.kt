package com.example.test

androidx.test.espresso.Espresso.pressKey
androidx.test.espresso.action.ViewActions.clearText
androidx.test.espresso.action.ViewActions.click
androidx.test.espresso.action.ViewActions.doubleClick
androidx.test.espresso.action.ViewActions.longClick
androidx.test.espresso.action.ViewActions.scrollTo
androidx.test.espresso.action.ViewActions.swipe
androidx.test.espresso.action.ViewActions.swipeUp
androidx.test.espresso.action.ViewActions.typeText
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
 * Scenario: all_actions_test
 * Generated on: 2025-01-01T10:00:00Z
 *
 * Original scenario file: Unknown
 */
@RunWith(AndroidJUnit4::class)
class AllActionsTestTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testScenario() {
        // Generated from scenario: all_actions_test
        // Created: 2025-01-01T10:00:00Z
        
        // Action 1: click
        onView(withText("Button")).perform(click())

        // Action 2: click_xpath
        onView(withText("Item")).perform(click())

        // Action 3: send_text
        onView(withText("")).perform(clearText(), typeText("input"))

        // Action 4: long_click
        onView(withText("Item")).perform(longClick())

        // Action 5: double_click
        onView(withText("Item")).perform(doubleClick())

        // Action 6: click_at
        perform(clickXY(100, 200))

        // Action 7: swipe
        perform(swipe(100, 500, 100, 100))

        // Action 8: scroll_to
        perform(scrollTo())

        // Action 9: scroll_forward
        perform(swipeUp())

        // Action 10: press_key
        pressKey("back")

    }
}
