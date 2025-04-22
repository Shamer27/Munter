import { StyleSheet, Text, View } from 'react-native'
import React from 'react'
import { useLocalSearchParams } from 'expo-router'

const Drinks  = () => {
    const { id } = useLocalSearchParams();
  return (
    <View>
      <Text>Flavour {id} </Text>
    </View>
  )
}

export default Drinks;

const styles = StyleSheet.create({})