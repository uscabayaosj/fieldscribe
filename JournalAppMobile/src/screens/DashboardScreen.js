import React from 'react';
import { View, Text, FlatList, TouchableOpacity, StyleSheet } from 'react-native';

const DashboardScreen = ({ navigation }) => {
  // TODO: Fetch actual entries from the backend
  const entries = [
    { id: '1', title: 'My First Entry', date: '2023-09-13' },
    { id: '2', title: 'Another Day', date: '2023-09-14' },
  ];

  const renderItem = ({ item }) => (
    <TouchableOpacity
      style={styles.entryItem}
      onPress={() => navigation.navigate('EntryForm', { entryId: item.id })}
    >
      <Text style={styles.entryTitle}>{item.title}</Text>
      <Text style={styles.entryDate}>{item.date}</Text>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Your Journal Entries</Text>
      <FlatList
        data={entries}
        renderItem={renderItem}
        keyExtractor={item => item.id}
      />
      <TouchableOpacity
        style={styles.addButton}
        onPress={() => navigation.navigate('EntryForm')}
      >
        <Text style={styles.addButtonText}>Add New Entry</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
  },
  title: {
    fontSize: 24,
    marginBottom: 20,
  },
  entryItem: {
    backgroundColor: 'white',
    padding: 15,
    borderRadius: 5,
    marginBottom: 10,
  },
  entryTitle: {
    fontSize: 18,
    fontWeight: 'bold',
  },
  entryDate: {
    color: 'gray',
  },
  addButton: {
    backgroundColor: 'blue',
    padding: 15,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 20,
  },
  addButtonText: {
    color: 'white',
    fontSize: 16,
  },
});

export default DashboardScreen;
