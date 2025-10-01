package com.example.test

androidx.test.espresso.action.ViewActions.clearText
androidx.test.espresso.action.ViewActions.click
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
 * Scenario: simple_login_test
 * Generated on: 2025-01-01T10:00:00Z
 *
 * Original scenario file: Unknown
 */
@RunWith(AndroidJUnit4::class)
class SimpleLoginTestTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun testScenario() {
        // Generated from scenario: simple_login_test
        // Created: 2025-01-01T10:00:00Z
        
        // Action 1: click
        onView(withText("Login")).perform(click())
        Thread.sleep(1000L)

        // Action 2: send_text
        Thread.sleep(500L)
        onView(withText("")).perform(clearText(), typeText("testuser@example.com"))
        Thread.sleep(500L)

        // Action 3: click_xpath
        Thread.sleep(1000L)
        onView(withText("Submit")).perform(click())
        Thread.sleep(2000L)

    }
}
