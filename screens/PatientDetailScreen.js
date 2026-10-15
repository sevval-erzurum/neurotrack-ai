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

import {
  createDoctorNote,
  getDoctorNotesForPatient,
  getPatientDetails,
} from "../services/api";

export default function PatientDetailScreen({
  patient,
  doctor,
  onBack,
  onOpenAnalysis,
}) {
  const [details, setDetails] = useState(null);
  const [doctorNotes, setDoctorNotes] = useState([]);

  const [note, setNote] = useState("");
  const [recommendation, setRecommendation] = useState("");
  const [nextVisitDate, setNextVisitDate] = useState("");

  async function loadDetails() {
    try {
      const { response, data } = await getPatientDetails(patient.id);

      if (response.ok) {
        setDetails(data);
      } else {
        Alert.alert("Detay hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function loadDoctorNotes() {
    try {
      const { response, data } = await getDoctorNotesForPatient(patient.id);

      if (response.ok) {
        setDoctorNotes(data);
      } else {
        Alert.alert("Doktor notu hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function handleSaveDoctorNote() {
    if (!note.trim()) {
      Alert.alert("Eksik bilgi", "Doktor notu boş olamaz.");
      return;
    }

    if (!recommendation.trim()) {
      Alert.alert("Eksik bilgi", "Öneri / takip planı boş olamaz.");
      return;
    }

    if (!nextVisitDate.trim()) {
      Alert.alert("Eksik bilgi", "Sonraki görüşme tarihi boş olamaz.");
      return;
    }

    try {
      const { response, data } = await createDoctorNote(
        doctor.user_id,
        patient.id,
        null,
        note,
        recommendation,
        nextVisitDate
      );

      if (response.ok) {
        Alert.alert("Başarılı", "Doktor notu kaydedildi.");

        setNote("");
        setRecommendation("");
        setNextVisitDate("");

        loadDoctorNotes();
      } else {
        Alert.alert("Kayıt hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  useEffect(() => {
    loadDetails();
    loadDoctorNotes();
  }, []);

  const predictions = details?.predictions || [];
  const dailyLogs = details?.daily_logs || [];

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>Hasta Detayı</Text>

        <View style={styles.patientCard}>
          <Text style={styles.patientName}>{patient.name}</Text>
          <Text style={styles.text}>ID: {patient.id}</Text>
          <Text style={styles.text}>Email: {patient.email}</Text>
        </View>

        <Pressable style={styles.refreshButton} onPress={loadDetails}>
          <Text style={styles.buttonText}>Verileri Yenile</Text>
        </Pressable>

        <Pressable
          style={styles.analysisButton}
          onPress={() => onOpenAnalysis(patient)}
        >
          <Text style={styles.buttonText}>AI Hasta Analizi</Text>
        </Pressable>

        <Text style={styles.sectionTitle}>Tahmin Geçmişi</Text>

        {predictions.length === 0 ? (
          <Text style={styles.emptyText}>Tahmin kaydı yok.</Text>
        ) : (
          predictions.map((item, index) => (
            <View key={index} style={styles.card}>
              <Text style={styles.cardTitle}>
                Sonuç: {item.result === 1 ? "Risk Var" : "Risk Yok"}
              </Text>
              <Text style={styles.text}>Yaş: {item.age}</Text>
              <Text style={styles.dateText}>Tarih: {item.created_at || "-"}</Text>
            </View>
          ))
        )}

        <Text style={styles.sectionTitle}>Günlük Kayıtlar</Text>

        {dailyLogs.length === 0 ? (
          <Text style={styles.emptyText}>Günlük kayıt yok.</Text>
        ) : (
          dailyLogs.map((item, index) => (
            <View key={index} style={styles.card}>
              <Text style={styles.cardTitle}>Duygu: {item.mood}</Text>
              <Text style={styles.text}>Uyku: {item.sleep} saat</Text>
              <Text style={styles.text}>Sosyal: {item.social}/10</Text>
              <Text style={styles.text}>Not: {item.note}</Text>
              <Text style={styles.dateText}>Tarih: {item.created_at || "-"}</Text>
            </View>
          ))
        )}

        <Text style={styles.sectionTitle}>Doktor Notu Ekle</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Doktor Gözlem Notu</Text>
          <TextInput
            placeholder="Hasta hakkında gözlem notu yaz"
            placeholderTextColor="#6B7280"
            value={note}
            onChangeText={setNote}
            style={styles.textArea}
            multiline
          />

          <Text style={styles.label}>Öneri / Takip Planı</Text>
          <TextInput
            placeholder="Önerilen terapi, takip planı veya yönlendirme"
            placeholderTextColor="#6B7280"
            value={recommendation}
            onChangeText={setRecommendation}
            style={styles.textArea}
            multiline
          />

          <Text style={styles.label}>Sonraki Görüşme Tarihi</Text>
          <TextInput
            placeholder="Örn: 2026-05-20"
            placeholderTextColor="#6B7280"
            value={nextVisitDate}
            onChangeText={setNextVisitDate}
            style={styles.input}
          />

          <Pressable style={styles.saveButton} onPress={handleSaveDoctorNote}>
            <Text style={styles.buttonText}>Doktor Notunu Kaydet</Text>
          </Pressable>
        </View>

        <Text style={styles.sectionTitle}>Doktor Notları</Text>

        <Pressable style={styles.refreshButton} onPress={loadDoctorNotes}>
          <Text style={styles.buttonText}>Notları Yenile</Text>
        </Pressable>

        {doctorNotes.length === 0 ? (
          <Text style={styles.emptyText}>Bu hasta için doktor notu yok.</Text>
        ) : (
          doctorNotes.map((item, index) => (
            <View key={index} style={styles.noteCard}>
              <Text style={styles.cardTitle}>Doktor Notu</Text>
              <Text style={styles.text}>Not: {item.note}</Text>
              <Text style={styles.text}>Öneri: {item.recommendation}</Text>
              <Text style={styles.text}>
                Sonraki görüşme: {item.next_visit_date}
              </Text>
              <Text style={styles.dateText}>Tarih: {item.created_at || "-"}</Text>
            </View>
          ))
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
    marginBottom: 16,
  },
  patientCard: {
    backgroundColor: "#EFF6FF",
    padding: 16,
    borderRadius: 14,
    marginBottom: 14,
  },
  patientName: {
    fontSize: 20,
    fontWeight: "700",
    color: "#2563EB",
    marginBottom: 6,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "700",
    color: "#111827",
    marginTop: 18,
    marginBottom: 10,
  },
  card: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderRadius: 14,
    marginBottom: 10,
  },
  noteCard: {
    backgroundColor: "#F0FDF4",
    padding: 16,
    borderRadius: 14,
    marginBottom: 10,
  },
  cardTitle: {
    fontSize: 17,
    fontWeight: "700",
    color: "#111827",
    marginBottom: 6,
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
    minHeight: 85,
    marginBottom: 12,
    color: "#111827",
  },
  text: {
    fontSize: 14,
    color: "#374151",
    marginBottom: 4,
    lineHeight: 20,
  },
  dateText: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 4,
  },
  emptyText: {
    color: "#6B7280",
    marginBottom: 10,
  },
  refreshButton: {
    backgroundColor: "#059669",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 10,
  },
  analysisButton: {
    backgroundColor: "#7C3AED",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 10,
  },
  saveButton: {
    backgroundColor: "#2563EB",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 4,
  },
  backButton: {
    backgroundColor: "#374151",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 18,
    marginBottom: 24,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },
});