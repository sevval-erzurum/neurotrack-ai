import { useState } from "react";
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

import { createChildClinicalFollowUp } from "../services/api";

export default function ChildClinicalScreen({ child, onBack }) {
  const [meltdown, setMeltdown] = useState("Hayır");
  const [sensorySensitivity, setSensorySensitivity] = useState("5");
  const [eyeContact, setEyeContact] = useState("5");
  const [communicationWillingness, setCommunicationWillingness] = useState("5");
  const [routineReaction, setRoutineReaction] = useState("5");
  const [eatingPattern, setEatingPattern] = useState("Normal");
  const [medicationTherapy, setMedicationTherapy] = useState("");
  const [note, setNote] = useState("");

  function validateScore(value, fieldName) {
    const numberValue = Number(value);

    if (Number.isNaN(numberValue) || numberValue < 0 || numberValue > 10) {
      Alert.alert("Hatalı değer", `${fieldName} 0-10 arasında sayı olmalı.`);
      return null;
    }

    return numberValue;
  }

  async function handleSave() {
    const sensoryNumber = validateScore(sensorySensitivity, "Duyusal hassasiyet");
    const eyeNumber = validateScore(eyeContact, "Göz teması");
    const communicationNumber = validateScore(
      communicationWillingness,
      "İletişim isteği"
    );
    const routineNumber = validateScore(routineReaction, "Rutin değişikliğine tepki");

    if (
      sensoryNumber === null ||
      eyeNumber === null ||
      communicationNumber === null ||
      routineNumber === null
    ) {
      return;
    }

    try {
      const { response, data } = await createChildClinicalFollowUp(
        child.id,
        meltdown,
        sensoryNumber,
        eyeNumber,
        communicationNumber,
        routineNumber,
        eatingPattern,
        medicationTherapy,
        note
      );

      if (response.ok) {
        Alert.alert("Başarılı", "Çocuk klinik takip kaydı eklendi.");

        setMeltdown("Hayır");
        setSensorySensitivity("5");
        setEyeContact("5");
        setCommunicationWillingness("5");
        setRoutineReaction("5");
        setEatingPattern("Normal");
        setMedicationTherapy("");
        setNote("");
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
        <Text style={styles.title}>Çocuk Klinik Takip</Text>
        <Text style={styles.childName}>{child.name}</Text>

        <View style={styles.card}>
          <Text style={styles.label}>Kriz / Meltdown</Text>
          <TextInput
            placeholder="Hayır / Evet / Kısmen"
            placeholderTextColor="#6B7280"
            value={meltdown}
            onChangeText={setMeltdown}
            style={styles.input}
          />

          <Text style={styles.label}>Duyusal Hassasiyet 0-10</Text>
          <TextInput
            value={sensorySensitivity}
            onChangeText={setSensorySensitivity}
            keyboardType="numeric"
            style={styles.input}
          />

          <Text style={styles.label}>Göz Teması 0-10</Text>
          <TextInput
            value={eyeContact}
            onChangeText={setEyeContact}
            keyboardType="numeric"
            style={styles.input}
          />

          <Text style={styles.label}>İletişim Kurma İsteği 0-10</Text>
          <TextInput
            value={communicationWillingness}
            onChangeText={setCommunicationWillingness}
            keyboardType="numeric"
            style={styles.input}
          />

          <Text style={styles.label}>Rutin Değişikliğine Tepki 0-10</Text>
          <TextInput
            value={routineReaction}
            onChangeText={setRoutineReaction}
            keyboardType="numeric"
            style={styles.input}
          />

          <Text style={styles.label}>Yemek Düzeni</Text>
          <TextInput
            placeholder="Normal / Az yedi / Seçici yeme / Düzensiz"
            placeholderTextColor="#6B7280"
            value={eatingPattern}
            onChangeText={setEatingPattern}
            style={styles.input}
          />

          <Text style={styles.label}>Terapi / İlaç Bilgisi</Text>
          <TextInput
            placeholder="Varsa yaz"
            placeholderTextColor="#6B7280"
            value={medicationTherapy}
            onChangeText={setMedicationTherapy}
            style={styles.input}
          />

          <Text style={styles.label}>Klinik Not</Text>
          <TextInput
            placeholder="Ek not"
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
    marginBottom: 24,
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
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },
});