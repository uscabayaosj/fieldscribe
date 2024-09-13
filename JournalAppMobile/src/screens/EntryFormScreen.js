import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';

const EntryFormScreen = ({ route, navigation }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [location, setLocation] = useState('');

  const entryId = route.params?.entryId;

  useEffect(() => {
    if (entryId) {
      // TODO: Fetch entry data from backend
      // For now, we'll use dummy data
      setTitle('Dummy Title');
      setContent('Dummy Content');
      setLocation('Dummy Location');
    }
  }, [entryId]);

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving entry:', { title, content, location });
    navigation.goBack();
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{entryId ? 'Edit Entry' : 'New Entry'}</Text>
      <TextInput
        style={styles.input}
        placeholder="Title"
        value={title}
        onChangeText={setTitle}
      />
      <TextInput
        style={[styles.input, styles.contentInput]}
        placeholder="Content"
        value={content}
        onChangeText={setContent}
        multiline
      />
      <TextInput
        style={styles.input}
        placeholder="Location"
        value={location}
        onChangeText={setLocation}
      />
      <TouchableOpacity style={styles.button} onPress={handleSave}>
        <Text style={styles.buttonText}>Save Entry</Text>
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
  input: {
    width: '100%',
    height: 40,
    borderColor: 'gray',
    borderWidth: 1,
    marginBottom: 10,
    paddingHorizontal: 10,
  },
  contentInput: {
    height: 120,
    textAlignVertical: 'top',
  },
  button: {
    backgroundColor: 'blue',
    padding: 15,
    borderRadius: 5,
    alignItems: 'center',
    marginTop: 20,
  },
  buttonText: {
    color: 'white',
    fontSize: 16,
  },
});

export default EntryFormScreen;
