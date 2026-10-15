import { useEffect, useState } from "react";
import {
    Alert,
    Pressable,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    View,
} from "react-native";

import { createChildDailyLog, getChildDailyLogs } from "../services/api";

export default function ChildDailyLogScreen({ child, onBack }) {
  const [mood, setMood] = useState("sakin");
  const [sleepHours, setSleepHours] = useState("8");
  const [socialInteraction, setSocialInteraction] = useState("5");
  const [note, setNote] = useState("");
  const [logs, setLogs] = useState([]);

  async function loadLogs() {
    try {
      const { response, data } = await getChildDailyLogs(child.id);

      if (response.ok) {
        setLogs(data);
      } else {
        Alert.alert("Listeleme hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  useEffect(() => {
    loadLogs();
  }, []);

  async function handleSave() {
    const sleepNumber = Number(sleepHours);
    const socialNumber = Number(socialInteraction);

    if (Number.isNaN(sleepNumber) || sleepNumber < 0 || sleepNumber > 24) {
      Alert.alert("Hatalı uyku saati", "Uyku saati 0-24 arasında sayı olmalı.");
      return;
    }

    if (Number.isNaN(socialNumber) || socialNumber < 0 || socialNumber > 10) {
      Alert.alert("Hatalı sosyal etkileşim", "Sosyal etkileşim 0-10 arasında sayı olmalı.");
      return;
    }

    try {
      const { response, data } = await createChildDailyLog(
        child.id,
        mood,
        sleepNumber,
        socialNumber,
        note
      );

      if (response.ok) {
        Alert.alert("Başarılı", "Çocuk günlük kaydı eklendi.");
        setMood("sakin");
        setSleepHours("8");
        setSocialInteraction("5");
        setNote("");
        loadLogs();
      } else {
        Alert.alert("Kayıt hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>Çocuk Günlük Kaydı</Text>
        <Text style={styles.childName}>{child.name}</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Duygu Durumu</Text>
          <TextInput
            placeholder="mutlu / üzgün / kaygılı / sakin / öfkeli"
            placeholderTextColor="#6B7280"
            value={mood}
            onChangeText={setMood}
            style={styles.input}
          />

          <Text style={styles.label}>Uyku Saati</Text>
          <TextInput
            placeholder="Örn: 8"
            placeholderTextColor="#6B7280"
            value={sleepHours}
            onChangeText={setSleepHours}
            keyboardType="numeric"
            style={styles.input}
          />

          <Text style={styles.label}>Sosyal Etkileşim 0-10</Text>
          <TextInput
            placeholder="Örn: 5"
            placeholderTextColor="#6B7280"
            value={socialInteraction}
            onChangeText={setSocialInteraction}
            keyboardType="numeric"
            style={styles.input}
          />

          <Text style={styles.label}>Not</Text>
          <TextInput
            placeholder="Bugün çocuk nasıl geçti?"
            placeholderTextColor="#6B7280"
            value={note}
            onChangeText={setNote}
            style={styles.textArea}
            multiline
          />

          <Pressable style={styles.button} onPress={handleSave}>
            <Text style={styles.buttonText}>Kaydet</Text>
          </Pressable>

          <Pressable style={styles.backButton} onPress={onBack}>
            <Text style={styles.buttonText}>Geri Dön</Text>
          </Pressable>
        </View>

        <Text style={styles.sectionTitle}>Çocuk Geçmiş Günlük Kayıtları</Text>

        <Pressable style={styles.refreshButton} onPress={loadLogs}>
          <Text style={styles.buttonText}>Listeyi Yenile</Text>
        </Pressable>

        {logs.length === 0 ? (
          <Text style={styles.emptyText}>Henüz günlük kayıt yok.</Text>
        ) : (
          logs.map((log) => (
            <View key={log.id} style={styles.logCard}>
              <Text style={styles.logTitle}>Duygu: {log.mood}</Text>
              <Text style={styles.logText}>Uyku: {log.sleep_hours} saat</Text>
              <Text style={styles.logText}>
                Sosyal Etkileşim: {log.social_interaction}/10
              </Text>
              <Text style={styles.logText}>Not: {log.note}</Text>
              <Text style={styles.dateText}>
                Tarih: {log.created_at || "-"}
              </Text>
            </View>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    color: "#111827",
    textAlign: "center",
    marginBottom: 8,
  },
  childName: {
    fontSize: 20,
    fontWeight: "700",
    color: "#2563EB",
    textAlign: "center",
    marginBottom: 16,
  },
  card: {
    backgroundColor: "#FFFFFF",
    padding: 18,
    borderRadius: 16,
    marginBottom: 20,
  },
  label: {
    fontSize: 14,
    fontWeight: "700",
    color: "#374151",
    marginBottom: 6,
  },
  input: {
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
    color: "#111827",
  },
  textArea: {
    backgroundColor: "#FFFFFF",
    borderWidth: 1,
    borderColor: "#CBD5E1",
    borderRadius: 12,
    padding: 12,
    minHeight: 90,
    marginBottom: 12,
    color: "#111827",
  },
  button: {
    backgroundColor: "#2563EB",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 8,
  },
  backButton: {
    backgroundColor: "#374151",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 10,
  },
  refreshButton: {
    backgroundColor: "#059669",
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 12,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#111827",
    marginBottom: 10,
  },
  emptyText: {
    textAlign: "center",
    color: "#6B7280",
    marginTop: 10,
  },
  logCard: {
    backgroundColor: "#FFFFFF",
    padding: 14,
    borderRadius: 14,
    marginBottom: 10,
  },
  logTitle: {
    fontSize: 16,
    fontWeight: "700",
    color: "#111827",
    marginBottom: 6,
  },
  logText: {
    fontSize: 14,
    color: "#374151",
    marginBottom: 4,
  },
  dateText: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 4,
  },
});