import { Text, View, StyleSheet } from 'react-native';
import { Link } from 'expo-router';

export default function Index() {
  return (
    <View style={styles.container}>"
      <Text style={styles.text}>Balls</Text>
      <Link href="/onboarding">Onboarding</Link>
      <Link href="/drink/flavour1">Your Top Flavour</Link>
    </View>
  );
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