import { useEffect, useState } from "react";
import {
    Alert,
    Pressable,
    SafeAreaView,
    ScrollView,
    StyleSheet,
    Text,
    View,
} from "react-native";

import { getChildAlerts } from "../services/api";

export default function ChildAlertScreen({ child, onBack }) {
  const [alerts, setAlerts] = useState([]);

  async function loadAlerts() {
    try {
      const { response, data } = await getChildAlerts(child.id);

      if (response.ok) {
        setAlerts(data.alerts || []);
      } else {
        Alert.alert("Uyarı hatası", JSON.stringify(data));
      }
    } catch (error) {
      Alert.alert("Bağlantı hatası", String(error));
    }
  }

  useEffect(() => {
    loadAlerts();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>Çocuk Uyarı Analizi</Text>
        <Text style={styles.childName}>{child.name}</Text>

        <Text style={styles.info}>
          Bu ekran çocuğun günlük ve klinik kayıtlarına göre takip uyarısı üretir.
          Tanı koymaz.
        </Text>

        <Pressable style={styles.button} onPress={loadAlerts}>
          <Text style={styles.buttonText}>Uyarıları Yenile</Text>
        </Pressable>

        {alerts.length === 0 ? (
          <View style={styles.safeBox}>
            <Text style={styles.text}>Henüz uyarı yok.</Text>
          </View>
        ) : (
          alerts.map((item, index) => {
            const isSafe = item.includes("belirgin bir takip uyarısı görünmüyor");

            return (
              <View key={index} style={isSafe ? styles.safeBox : styles.alertBox}>
                <Text style={styles.text}>{item}</Text>
              </View>
            );
          })
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
    marginBottom: 8,
  },
  childName: {
    fontSize: 20,
    fontWeight: "700",
    color: "#2563EB",
    textAlign: "center",
    marginBottom: 12,
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
    marginTop: 16,
    marginBottom: 24,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "700",
  },
  alertBox: {
    backgroundColor: "#FECACA",
    padding: 16,
    borderRadius: 14,
    marginBottom: 10,
  },
  safeBox: {
    backgroundColor: "#DCFCE7",
    padding: 16,
    borderRadius: 14,
    marginBottom: 10,
  },
  text: {
    color: "#111827",
    fontSize: 15,
    lineHeight: 22,
  },
});