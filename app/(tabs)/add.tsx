import { View, Text, StyleSheet } from 'react-native'
import React from 'react'

const add = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Add</Text>
    </View>
  )
}


const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  text: {
    fontSize: 40,
    color: '#3b82fc',  
    fontWeight: 'bold',
  },
});
export default add