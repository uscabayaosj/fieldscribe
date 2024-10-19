import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet, Image } from 'react-native';
import * as ImagePicker from 'expo-image-picker';

const EntryFormScreen = ({ route, navigation }) => {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [location, setLocation] = useState('');
  const [photo, setPhoto] = useState(null);

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

  const handleSave = async () => {
    // TODO: Implement save functionality
    const formData = new FormData();
    formData.append('title', title);
    formData.append('content', content);
    formData.append('location', location);
    if (photo) {
      formData.append('photo', {
        uri: photo,
        type: 'image/jpeg',
        name: 'photo.jpg',
      });
    }

    try {
      const response = await fetch('YOUR_API_ENDPOINT', {
        method: 'POST',
        body: formData,
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.ok) {
        console.log('Entry saved successfully');
        navigation.goBack();
      } else {
        console.error('Failed to save entry');
      }
    } catch (error) {
      console.error('Error saving entry:', error);
    }
  };

  const handleTakePhoto = async () => {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    
    if (permissionResult.granted === false) {
      alert("You've refused to allow this app to access your camera!");
      return;
    }

    const result = await ImagePicker.launchCameraAsync({
      allowsEditing: true,
      aspect: [4, 3],
      quality: 1,
    });

    if (!result.canceled) {
      setPhoto(result.assets[0].uri);
    }
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
      <TouchableOpacity style={styles.button} onPress={handleTakePhoto}>
        <Text style={styles.buttonText}>Take Photo</Text>
      </TouchableOpacity>
      {photo && <Image source={{ uri: photo }} style={styles.photo} />}
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
  photo: {
    width: '100%',
    height: 200,
    resizeMode: 'cover',
    marginTop: 20,
  },
});

export default EntryFormScreen;
