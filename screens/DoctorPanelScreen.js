import { useEffect, useState } from "react";
import {
  Alert,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
} from "react-native";

import {
  addChildPatientToDoctor,
  addPatientToDoctor,
  getMyChildPatients,
  getMyPatients,
  removeChildPatientFromDoctor,
  removePatientFromDoctor,
} from "../services/api";

export default function DoctorPanelScreen({
  user,
  onBack,
  onOpenPatient,
  onOpenChildPatient,
}) {
  const [adultPatients, setAdultPatients] = useState([]);
  const [childPatients, setChildPatients] = useState([]);

  const [patientId, setPatientId] = useState("");
  const [childId, setChildId] = useState("");

  async function loadPatients() {
    try {
      const adultResult = await getMyPatients(user.user_id);
      const childResult = await getMyChildPatients(user.user_id);

      if (adultResult.response.ok) {
        setAdultPatients(adultResult.data);
      } else {
        Alert.alert("Yetişkin hasta hatası", JSON.stringify(adultResult.data));
      }

      if (childResult.response.ok) {
        setChildPatients(childResult.data);
      } else {
        Alert.alert("Çocuk hasta hatası", JSON.stringify(childResult.data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function handleAddPatient() {
    const numberId = Number(patientId);

    if (Number.isNaN(numberId) || numberId <= 0) {
      Alert.alert("Hata", "Geçerli bir hasta ID gir.");
      return;
    }

    try {
      const { response, data } = await addPatientToDoctor(
        user.user_id,
        numberId
      );

      if (response.ok) {
        Alert.alert("Başarılı", "Hasta eklendi.");
        setPatientId("");
        loadPatients();
      } else {
        Alert.alert(
          "Ekleme hatası",
          data.detail ? String(data.detail) : JSON.stringify(data)
        );
      }
    } catch (e) {
      Alert.alert("Bağlantı hatası", String(e));
    }
  }

  async function handleAddChildPatient() {
    const numberId = Number(childId);

    if (Number.isNaN(numberId) || numberId <= 0) {
      Alert.alert("Hata", "Geçerli bir çocuk ID gir.");
      return;
    }

    try {
      const { response, data } = await addChildPatientToDoctor(
        user.user_id,
        numberId
      );

      if (response.ok) {
        Alert.alert("Başarılı", "Çocuk hasta eklendi.");
        setChildId("");
        loadPatients();
      } else {
        Alert.alert(
          "Ekleme hatası",
          data.detail ? String(data.detail) : JSON.stringify(data)
        );
      }
    } catch (e) {
      Alert.alert("Bağlantı hatası", String(e));
    }
  }

  function confirmRemovePatient(patient) {
    Alert.alert(
      "Hastayı Listeden Çıkar",
      `${patient.name} adlı hastayı doktor listenizden çıkarmak istediğinize emin misiniz? Hasta hesabı silinmez.`,
      [
        { text: "Vazgeç", style: "cancel" },
        {
          text: "Çıkar",
          style: "destructive",
          onPress: () => handleRemovePatient(patient),
        },
      ]
    );
  }

  async function handleRemovePatient(patient) {
    try {
      const { response, data } = await removePatientFromDoctor(
        user.user_id,
        patient.id
      );

      if (response.ok) {
        Alert.alert("Başarılı", "Hasta doktor listesinden çıkarıldı.");
        loadPatients();
      } else {
        Alert.alert(
          "Çıkarma hatası",
          data.detail ? String(data.detail) : JSON.stringify(data)
        );
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  function confirmRemoveChildPatient(child) {
    Alert.alert(
      "Çocuk Hastayı Listeden Çıkar",
      `${child.name} adlı çocuk hastayı doktor listenizden çıkarmak istediğinize emin misiniz? Çocuk kaydı sistemden silinmez.`,
      [
        { text: "Vazgeç", style: "cancel" },
        {
          text: "Çıkar",
          style: "destructive",
          onPress: () => handleRemoveChildPatient(child),
        },
      ]
    );
  }

  async function handleRemoveChildPatient(child) {
    try {
      const { response, data } = await removeChildPatientFromDoctor(
        user.user_id,
        child.id
      );

      if (response.ok) {
        Alert.alert("Başarılı", "Çocuk hasta doktor listesinden çıkarıldı.");
        loadPatients();
      } else {
        Alert.alert(
          "Çıkarma hatası",
          data.detail ? String(data.detail) : JSON.stringify(data)
        );
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  useEffect(() => {
    loadPatients();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>Doktor Paneli</Text>

        <Pressable style={styles.refreshButton} onPress={loadPatients}>
          <Text style={styles.buttonText}>Listeyi Yenile</Text>
        </Pressable>

        <Text style={styles.sectionTitle}>Yetişkin Hasta Ekle</Text>

        <TextInput
          placeholder="Hasta kullanıcı ID"
          placeholderTextColor="#6B7280"
          value={patientId}
          onChangeText={setPatientId}
          keyboardType="numeric"
          style={styles.input}
        />

        <Pressable style={styles.button} onPress={handleAddPatient}>
          <Text style={styles.buttonText}>Hasta Ekle</Text>
        </Pressable>

        <Text style={styles.sectionTitle}>Çocuk Hasta Ekle</Text>

        <TextInput
          placeholder="Çocuk ID"
          placeholderTextColor="#6B7280"
          value={childId}
          onChangeText={setChildId}
          keyboardType="numeric"
          style={styles.input}
        />

        <Pressable style={styles.button} onPress={handleAddChildPatient}>
          <Text style={styles.buttonText}>Çocuk Hasta Ekle</Text>
        </Pressable>

        <Text style={styles.sectionTitle}>Yetişkin Hastalar</Text>

        {adultPatients.length === 0 ? (
          <Text style={styles.emptyText}>Kayıtlı yetişkin hasta yok.</Text>
        ) : (
          adultPatients.map((patient) => (
            <Pressable
              key={patient.id}
              style={styles.card}
              onPress={() => onOpenPatient(patient)}
            >
              <Text style={styles.cardTitle}>{patient.name}</Text>
              <Text style={styles.cardText}>ID: {patient.id}</Text>
              <Text style={styles.cardText}>Email: {patient.email}</Text>
              <Text style={styles.detailText}>Detay için karta dokun</Text>

              <Pressable
                style={styles.removeButton}
                onPress={() => confirmRemovePatient(patient)}
              >
                <Text style={styles.buttonText}>Listeden Çıkar</Text>
              </Pressable>
            </Pressable>
          ))
        )}

        <Text style={styles.sectionTitle}>Çocuk Hastalar</Text>

        {childPatients.length === 0 ? (
          <Text style={styles.emptyText}>Kayıtlı çocuk hasta yok.</Text>
        ) : (
          childPatients.map((child) => (
            <Pressable
              key={child.id}
              style={styles.card}
              onPress={() => onOpenChildPatient(child)}
            >
              <Text style={styles.cardTitle}>{child.name}</Text>
              <Text style={styles.cardText}>ID: {child.id}</Text>
              <Text style={styles.cardText}>Yaş: {child.age}</Text>
              <Text style={styles.cardText}>Cinsiyet: {child.gender}</Text>
              <Text style={styles.cardText}>Ebeveyn: {child.parent_name}</Text>
              <Text style={styles.detailText}>Detay için karta dokun</Text>

              <Pressable
                style={styles.removeButton}
                onPress={() => confirmRemoveChildPatient(child)}
              >
                <Text style={styles.buttonText}>Listeden Çıkar</Text>
              </Pressable>
            </Pressable>
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
    padding: 20,
    backgroundColor: "#F3F4F6",
  },
  title: {
    fontSize: 24,
    fontWeight: "900",
    textAlign: "center",
    marginBottom: 16,
    color: "#111827",
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "900",
    marginTop: 20,
    marginBottom: 8,
    color: "#111827",
  },
  input: {
    backgroundColor: "#FFFFFF",
    padding: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#CBD5E1",
    marginBottom: 10,
    color: "#111827",
  },
  button: {
    backgroundColor: "#2563EB",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
  },
  refreshButton: {
    backgroundColor: "#059669",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
    marginBottom: 8,
  },
  removeButton: {
    backgroundColor: "#DC2626",
    padding: 11,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },
  buttonText: {
    color: "#FFFFFF",
    fontWeight: "900",
  },
  card: {
    backgroundColor: "#FFFFFF",
    padding: 14,
    borderRadius: 12,
    marginBottom: 10,
  },
  cardTitle: {
    fontWeight: "900",
    fontSize: 17,
    color: "#2563EB",
    marginBottom: 5,
  },
  cardText: {
    fontSize: 14,
    color: "#374151",
    marginBottom: 3,
  },
  detailText: {
    color: "#2563EB",
    fontSize: 13,
    fontWeight: "800",
    marginTop: 6,
  },
  emptyText: {
    color: "#6B7280",
    marginBottom: 10,
  },
  backButton: {
    marginTop: 20,
    marginBottom: 24,
    backgroundColor: "#374151",
    padding: 14,
    borderRadius: 10,
    alignItems: "center",
  },
});