import { useEffect, useState } from "react";
import {
  Alert,
  Dimensions,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { LineChart } from "react-native-chart-kit";
import { getDailyLogs } from "../services/api";

const screenWidth = Dimensions.get("window").width;

export default function AnalyticsScreen({ user, onBack }) {
  const [logs, setLogs] = useState([]);

  async function loadLogs() {
    try {
      const { response, data } = await getDailyLogs(user.user_id);

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

  function getChartData(field) {
    if (!logs || logs.length === 0) {
      return [0];
    }

    return logs.map((log) => {
      const value = log[field];

      if (value === undefined || value === null) {
        return 0;
      }

      return Number(value);
    });
  }

  function getLabels() {
    if (!logs || logs.length === 0) {
      return ["-"];
    }

    return logs.map((_, index) => `G${index + 1}`);
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView>
        <Text style={styles.title}>Gelişim Grafiği</Text>

        <View style={styles.infoBox}>
          <Text style={styles.infoText}>
            Bu grafikler günlük kayıtlarına göre oluşturulur.
          </Text>
          <Text style={styles.infoText}>
            Kayıt sayısı arttıkça gelişim eğilimi daha anlamlı görünür.
          </Text>
        </View>

        <Pressable style={styles.refreshButton} onPress={loadLogs}>
          <Text style={styles.buttonText}>Grafikleri Yenile</Text>
        </Pressable>

        {logs.length === 0 ? (
          <View style={styles.emptyBox}>
            <Text style={styles.emptyText}>
              Henüz günlük kayıt yok. Grafik oluşması için önce günlük kayıt gir.
            </Text>
          </View>
        ) : (
          <>
            <Text style={styles.chartTitle}>Uyku Saatleri</Text>

            <LineChart
              data={{
                labels: getLabels(),
                datasets: [{ data: getChartData("sleep_hours") }],
              }}
              width={screenWidth - 40}
              height={220}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />

            <Text style={styles.chartTitle}>Sosyal Etkileşim</Text>

            <LineChart
              data={{
                labels: getLabels(),
                datasets: [{ data: getChartData("social_interaction") }],
              }}
              width={screenWidth - 40}
              height={220}
              chartConfig={chartConfig}
              bezier
              style={styles.chart}
            />
          </>
        )}

        <Pressable style={styles.backButton} onPress={onBack}>
          <Text style={styles.buttonText}>Geri Dön</Text>
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

const chartConfig = {
  backgroundGradientFrom: "#FFFFFF",
  backgroundGradientTo: "#FFFFFF",
  decimalPlaces: 1,
  color: (opacity = 1) => `rgba(37, 99, 235, ${opacity})`,
  labelColor: (opacity = 1) => `rgba(17, 24, 39, ${opacity})`,
};

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
    marginBottom: 14,
  },
  infoBox: {
    backgroundColor: "#EFF6FF",
    padding: 14,
    borderRadius: 14,
    marginBottom: 14,
  },
  infoText: {
    color: "#2563EB",
    fontSize: 13,
    lineHeight: 20,
    fontWeight: "700",
    textAlign: "center",
  },
  refreshButton: {
    backgroundColor: "#059669",
    padding: 13,
    borderRadius: 12,
    alignItems: "center",
    marginBottom: 14,
  },
  chartTitle: {
    fontSize: 18,
    fontWeight: "900",
    color: "#111827",
    marginTop: 18,
    marginBottom: 8,
  },
  chart: {
    borderRadius: 16,
    marginBottom: 10,
  },
  emptyBox: {
    backgroundColor: "#FFFFFF",
    padding: 18,
    borderRadius: 16,
    marginTop: 10,
  },
  emptyText: {
    color: "#6B7280",
    textAlign: "center",
    lineHeight: 20,
  },
  backButton: {
    backgroundColor: "#374151",
    padding: 14,
    borderRadius: 12,
    alignItems: "center",
    marginTop: 20,
    marginBottom: 24,
  },
  buttonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "900",
  },
});