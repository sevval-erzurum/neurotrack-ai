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

import { getPatientAnalysis } from "../services/api";

export default function PatientAnalysisScreen({ patient, onBack }) {
  const [analysis, setAnalysis] = useState(null);

  async function loadAnalysis() {
    try {
      const { response, data } = await getPatientAnalysis(patient.id);

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
        <Text style={styles.title}>Hasta AI Analizi</Text>

        <Text style={styles.patientName}>{patient.name}</Text>

        <Pressable style={styles.button} onPress={loadAnalysis}>
          <Text style={styles.buttonText}>Analiz Oluştur</Text>
        </Pressable>

        {analysis && analysis.summary && (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Genel Durum</Text>
            <Text style={styles.text}>{analysis.summary}</Text>
          </View>
        )}

        {analysis && analysis.risk_level && (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Risk Seviyesi</Text>
            <Text style={styles.text}>{analysis.risk_level}</Text>
          </View>
        )}

        {analysis && analysis.suggestions && (
          <View style={styles.card}>
            <Text style={styles.sectionTitle}>Öneriler</Text>

            {analysis.suggestions.map((item, index) => (
              <Text key={index} style={styles.text}>
                • {item}
              </Text>
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
    textAlign: "center",
    marginBottom: 10,
  },
  patientName: {
    fontSize: 20,
    fontWeight: "700",
    color: "#2563EB",
    textAlign: "center",
    marginBottom: 12,
  },
  button: {
    backgroundColor: "#2563EB",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 12,
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
    fontWeight: "700",
  },
  card: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderRadius: 14,
    marginBottom: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "700",
    marginBottom: 6,
  },
  text: {
    fontSize: 15,
    color: "#374151",
    marginBottom: 4,
  },
});