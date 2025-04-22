import { View, Text } from 'react-native'
import React from 'react'
import { Tabs } from 'expo-router'

const _layout = () => {
  return (
    <Tabs>
        <Tabs.Screen
            name="index"
            options={{
                title: 'Home',
                headerShown: false,
            }}
        />
        <Tabs.Screen   
            name="add"
            options={{
                title: 'Add',
                headerShown: false,
            }}
        />
        <Tabs.Screen
            name="ranks"
            options={{
                title: 'Ranks',
                headerShown: false,
            }}
        />
        <Tabs.Screen
            name="stats"
            options={{
                title: 'Stats',
                headerShown: false,
            }}
        />
    </Tabs>
  )
}

export default _layout