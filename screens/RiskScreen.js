import { useEffect, useState } from "react";
import {
    Pressable,
    SafeAreaView,
    StyleSheet,
    Text,
    View,
} from "react-native";

import { getRiskAlert } from "../services/api";

export default function RiskScreen({ user, onBack }) {
  const [risk, setRisk] = useState(null);

  async function loadRisk() {
    const { response, data } = await getRiskAlert(user.user_id);

    if (response.ok) {
      setRisk(data);
    }
  }

  useEffect(() => {
    loadRisk();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <Text style={styles.title}>Risk Analizi</Text>

      {risk && (
        <View
          style={
            risk.risk ? styles.riskBox : styles.safeBox
          }
        >
          <Text style={styles.text}>{risk.message}</Text>
        </View>
      )}

      <Pressable style={styles.button} onPress={loadRisk}>
        <Text style={styles.buttonText}>Tekrar Kontrol Et</Text>
      </Pressable>

      <Pressable style={styles.backButton} onPress={onBack}>
        <Text style={styles.buttonText}>Geri Dön</Text>
      </Pressable>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
    justifyContent: "center",
    alignItems: "center",
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: "700",
    marginBottom: 20,
  },
  riskBox: {
    backgroundColor: "#FECACA",
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
  },
  safeBox: {
    backgroundColor: "#BBF7D0",
    padding: 20,
    borderRadius: 12,
    marginBottom: 20,
  },
  text: {
    fontSize: 16,
    textAlign: "center",
  },
  button: {
    backgroundColor: "#2563EB",
    padding: 14,
    borderRadius: 12,
    marginBottom: 10,
  },
  backButton: {
    backgroundColor: "#374151",
    padding: 14,
    borderRadius: 12,
  },
  buttonText: {
    color: "#fff",
    fontWeight: "700",
  },
});