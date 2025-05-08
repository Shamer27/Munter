import { Text, View, StyleSheet } from 'react-native';
import React from 'react'

const ranks = () => {
  return (
    <View style={styles.container}>
      <Text style={styles.text}>Ranks</Text>
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
  }
});
export default ranks