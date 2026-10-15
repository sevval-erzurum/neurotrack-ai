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

import { createChild, deleteChild, getChildren } from "../services/api";

export default function ParentPanelScreen({
  user,
  onBack,
  onOpenChild,
  onOpenChildAlert,
  onOpenChildClinical,
}) {
  const [children, setChildren] = useState([]);
  const [name, setName] = useState("");
  const [age, setAge] = useState("7");
  const [gender, setGender] = useState("Kız");

  async function loadChildren() {
    try {
      const { response, data } = await getChildren(user.user_id);

      if (response.ok) {
        setChildren(data);
      } else {
        Alert.alert("Listeleme hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  async function handleCreateChild() {
    const ageNumber = Number(age);

    if (!name.trim()) {
      Alert.alert("Eksik bilgi", "Çocuk adı boş olamaz.");
      return;
    }

    if (Number.isNaN(ageNumber) || ageNumber < 1 || ageNumber > 18) {
      Alert.alert("Hatalı yaş", "Yaş 1-18 arasında olmalı.");
      return;
    }

    try {
      const { response, data } = await createChild(
        user.user_id,
        name,
        ageNumber,
        gender
      );

      if (response.ok) {
        Alert.alert("Başarılı", "Çocuk eklendi.");
        setName("");
        setAge("7");
        setGender("Kız");
        loadChildren();
      } else {
        Alert.alert("Kayıt hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  function confirmDeleteChild(child) {
    Alert.alert(
      "Çocuğu Sil",
      `${child.name} adlı çocuk kaydını silmek istediğine emin misin? Bu işlem çocuğun günlük ve klinik kayıtlarını da silebilir.`,
      [
        {
          text: "Vazgeç",
          style: "cancel",
        },
        {
          text: "Sil",
          style: "destructive",
          onPress: () => handleDeleteChild(child),
        },
      ]
    );
  }

  async function handleDeleteChild(child) {
    try {
      const { response, data } = await deleteChild(child.id, user.user_id);

      if (response.ok) {
        Alert.alert("Başarılı", "Çocuk kaydı silindi.");
        loadChildren();
      } else {
        Alert.alert(
          "Silme hatası",
          data.detail ? String(data.detail) : JSON.stringify(data)
        );
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  useEffect(() => {
    loadChildren();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>Ebeveyn Paneli</Text>

        <View style={styles.card}>
          <Text style={styles.sectionTitle}>Çocuk Ekle</Text>

          <TextInput
            placeholder="Çocuğun adı"
            placeholderTextColor="#6B7280"
            value={name}
            onChangeText={setName}
            style={styles.input}
          />

          <TextInput
            placeholder="Yaş"
            placeholderTextColor="#6B7280"
            value={age}
            onChangeText={setAge}
            keyboardType="numeric"
            style={styles.input}
          />

          <TextInput
            placeholder="Cinsiyet: Kız / Erkek"
            placeholderTextColor="#6B7280"
            value={gender}
            onChangeText={setGender}
            style={styles.input}
          />

          <Pressable style={styles.button} onPress={handleCreateChild}>
            <Text style={styles.buttonText}>Çocuğu Ekle</Text>
          </Pressable>
        </View>

        <Text style={styles.sectionTitle}>Çocuklarım</Text>

        <Pressable style={styles.refreshButton} onPress={loadChildren}>
          <Text style={styles.buttonText}>Listeyi Yenile</Text>
        </Pressable>

        {children.length === 0 ? (
          <Text style={styles.emptyText}>Henüz kayıtlı çocuk yok.</Text>
        ) : (
          children.map((child) => (
            <View key={child.id} style={styles.childCard}>
              <Text style={styles.childName}>{child.name}</Text>
              <Text style={styles.text}>ID: {child.id}</Text>
              <Text style={styles.text}>Yaş: {child.age}</Text>
              <Text style={styles.text}>Cinsiyet: {child.gender}</Text>
              <Text style={styles.dateText}>
                Tarih: {child.created_at || "-"}
              </Text>

              <Pressable
                style={styles.childActionButton}
                onPress={() => onOpenChild(child)}
              >
                <Text style={styles.buttonText}>Günlük Kayıt Gir</Text>
              </Pressable>

              <Pressable
                style={styles.clinicalButton}
                onPress={() => onOpenChildClinical(child)}
              >
                <Text style={styles.buttonText}>Klinik Takip Gir</Text>
              </Pressable>

              <Pressable
                style={styles.alertButton}
                onPress={() => onOpenChildAlert(child)}
              >
                <Text style={styles.buttonText}>Uyarı Analizi</Text>
              </Pressable>

              <Pressable
                style={styles.deleteButton}
                onPress={() => confirmDeleteChild(child)}
              >
                <Text style={styles.buttonText}>Çocuğu Sil</Text>
              </Pressable>
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
    fontWeight: "900",
    color: "#111827",
    textAlign: "center",
    marginBottom: 16,
  },
  card: {
    backgroundColor: "#FFFFFF",
    padding: 16,
    borderRadius: 16,
    marginBottom: 18,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: "900",
    color: "#111827",
    marginBottom: 10,
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
  button: {
    backgroundColor: "#2563EB",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
  },
  refreshButton: {
    backgroundColor: "#059669",
    padding: 12,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 12,
  },
  backButton: {
    backgroundColor: "#374151",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 18,
    marginBottom: 24,
  },
  childActionButton: {
    backgroundColor: "#2563EB",
    padding: 11,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 10,
  },
  clinicalButton: {
    backgroundColor: "#7C3AED",
    padding: 11,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 8,
  },
  alertButton: {
    backgroundColor: "#F59E0B",
    padding: 11,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 8,
  },
  deleteButton: {
    backgroundColor: "#DC2626",
    padding: 11,
    borderRadius: 10,
    alignItems: "center",
    marginTop: 8,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "900",
  },
  childCard: {
    backgroundColor: "#FFFFFF",
    padding: 14,
    borderRadius: 14,
    marginBottom: 10,
  },
  childName: {
    fontSize: 17,
    fontWeight: "900",
    color: "#2563EB",
    marginBottom: 6,
  },
  text: {
    fontSize: 14,
    color: "#374151",
    marginBottom: 4,
  },
  dateText: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 4,
  },
  emptyText: {
    color: "#6B7280",
    textAlign: "center",
    marginTop: 10,
  },
});