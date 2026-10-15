import { useState } from "react";
import {
    Alert,
    Pressable,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    View,
} from "react-native";

import { getDailyLogAnalysis } from "../services/api";

export default function AISuggestionScreen({ user, onBack }) {
  const [analysis, setAnalysis] = useState(null);

  async function loadAnalysis() {
    try {
      const { response, data } = await getDailyLogAnalysis(user.user_id);

      if (response.ok) {
        setAnalysis(data);
      } else {
        Alert.alert("Analiz hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>AI Günlük Öneri</Text>

        <Text style={styles.info}>
          Bu ekran son günlük kaydına göre destekleyici öneriler üretir. Tanı veya tedavi yerine geçmez.
        </Text>

        <Pressable style={styles.button} onPress={loadAnalysis}>
          <Text style={styles.buttonText}>Analiz Oluştur</Text>
        </Pressable>

        {analysis && analysis.message && (
          <View style={styles.card}>
            <Text style={styles.warningText}>{analysis.message}</Text>
          </View>
        )}

        {analysis && analysis.suggestions && (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Son Günlük Kaydın</Text>
            <Text style={styles.text}>Duygu Durumu: {analysis.latest_mood}</Text>
            <Text style={styles.text}>Uyku: {analysis.sleep_hours} saat</Text>
            <Text style={styles.text}>Sosyal Etkileşim: {analysis.social_interaction}/10</Text>
            <Text style={styles.text}>Not: {analysis.note}</Text>

            <Text style={styles.sectionTitle}>Öneriler</Text>
            {analysis.suggestions.map((item, index) => (
              <View key={index} style={styles.suggestionBox}>
                <Text style={styles.text}>{item}</Text>
              </View>
            ))}
          </View>
        )}

        <Pressable style={styles.backButton} onPress={onBack}>
          <Text style={styles.buttonText}>Geri Dön</Text>
        </Pressable>
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
    marginBottom: 10,
  },
  info: {
    fontSize: 13,
    color: "#6B7280",
    textAlign: "center",
    marginBottom: 16,
  },
  button: {
    backgroundColor: "#2563EB",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 14,
  },
  backButton: {
    backgroundColor: "#374151",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 12,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },
  card: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderRadius: 16,
    marginBottom: 14,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    color: "#111827",
    marginTop: 8,
    marginBottom: 8,
  },
  text: {
    fontSize: 15,
    color: "#374151",
    lineHeight: 22,
  },
  suggestionBox: {
    backgroundColor: "#EFF6FF",
    padding: 12,
    borderRadius: 12,
    marginBottom: 8,
  },
  warningText: {
    fontSize: 15,
    color: "#92400E",
  },
});