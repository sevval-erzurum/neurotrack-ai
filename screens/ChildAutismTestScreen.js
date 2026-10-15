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

import {
    createChildAutismTest,
    getChildAutismTests,
    getChildren,
} from "../services/api";

export default function ChildAutismTestScreen({ user }) {
  const [children, setChildren] = useState([]);
  const [selectedChild, setSelectedChild] = useState(null);
  const [answers, setAnswers] = useState({});
  const [testHistory, setTestHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const questions = [
    {
      key: "A1_Score",
      text: "Çocuk sosyal ortamlarda diğer çocuklarla etkileşim kurmakta zorlanıyor mu?",
    },
    {
      key: "A2_Score",
      text: "Göz teması kurmakta veya sürdürmekte zorlanıyor mu?",
    },
    {
      key: "A3_Score",
      text: "Rutin değişikliklerine karşı belirgin tepki gösteriyor mu?",
    },
    {
      key: "A4_Score",
      text: "İsmi söylendiğinde her zaman tepki vermiyor mu?",
    },
    {
      key: "A5_Score",
      text: "Tekrarlayan hareketler veya davranışlar gözlemleniyor mu?",
    },
    {
      key: "A6_Score",
      text: "Ses, ışık, kalabalık gibi duyusal uyaranlardan fazla etkileniyor mu?",
    },
    {
      key: "A7_Score",
      text: "Yaşıtlarına göre iletişim kurma isteği düşük mü?",
    },
    {
      key: "A8_Score",
      text: "Oyuncakları amacına uygun oynamak yerine sıralama/döndürme gibi davranışlar gösteriyor mu?",
    },
    {
      key: "A9_Score",
      text: "Duygularını ifade etmekte veya karşı tarafın duygularını anlamakta zorlanıyor mu?",
    },
    {
      key: "A10_Score",
      text: "Belirli nesne, konu veya davranışlara yoğun şekilde takılıyor mu?",
    },
  ];

  async function loadChildren() {
    try {
      const { response, data } = await getChildren(user.user_id);

      if (response.ok) {
        setChildren(data);

        if (data.length > 0) {
          setSelectedChild(data[0]);
          loadHistory(data[0].id);
        }
      }
    } catch (error) {
      Alert.alert("Hata", "Çocuk bilgileri alınamadı.");
    }
  }

  async function loadHistory(childId) {
    try {
      const { response, data } = await getChildAutismTests(childId);

      if (response.ok) {
        setTestHistory(data);
      }
    } catch (error) {
      console.log("Çocuk test geçmişi alınamadı:", error);
    }
  }

  useEffect(() => {
    if (user.role === "parent") {
      loadChildren();
    }
  }, []);

  function setAnswer(questionKey, value) {
    setAnswers((prev) => ({
      ...prev,
      [questionKey]: value,
    }));
  }

  async function submitTest() {
    if (!selectedChild) {
      Alert.alert("Uyarı", "Önce bir çocuk seçmelisiniz.");
      return;
    }

    for (const question of questions) {
      if (answers[question.key] === undefined) {
        Alert.alert("Eksik Cevap", "Lütfen tüm soruları cevaplayın.");
        return;
      }
    }

    setLoading(true);

    try {
      const { response, data } = await createChildAutismTest(
        selectedChild.id,
        answers,
        selectedChild.age
      );

      if (response.ok) {
        Alert.alert(
          "Test Kaydedildi",
          `Risk düzeyi: ${data.risk_level}\n\n${data.result_text}`
        );

        setAnswers({});
        loadHistory(selectedChild.id);
      } else {
        Alert.alert("Hata", data.detail || "Test kaydedilemedi.");
      }
    } catch (error) {
      Alert.alert("Bağlantı Hatası", "Backend bağlantısı kontrol edilmelidir.");
    } finally {
      setLoading(false);
    }
  }

  if (user.role !== "parent") {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.card}>
          <Text style={styles.title}>Çocuk Otizm Testi</Text>
          <Text style={styles.emptyText}>
            Bu ekran sadece ebeveyn kullanıcılar içindir.
          </Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.headerCard}>
          <Text style={styles.title}>Çocuk Otizm Ön Tarama Testi</Text>
          <Text style={styles.subtitle}>
            Bu test tanı koymaz. Çocuğun davranışsal belirtilerini ön değerlendirme
            amacıyla takip eder.
          </Text>
        </View>

        {children.length === 0 ? (
          <View style={styles.card}>
            <Text style={styles.emptyText}>
              Henüz kayıtlı çocuk yok. Önce Parent Paneli üzerinden çocuk ekleyin.
            </Text>
          </View>
        ) : (
          <>
            <View style={styles.card}>
              <Text style={styles.sectionTitle}>Çocuk Seç</Text>

              {children.map((child) => (
                <Pressable
                  key={child.id}
                  style={[
                    styles.childButton,
                    selectedChild && selectedChild.id === child.id
                      ? styles.childButtonActive
                      : null,
                  ]}
                  onPress={() => {
                    setSelectedChild(child);
                    setAnswers({});
                    loadHistory(child.id);
                  }}
                >
                  <Text
                    style={[
                      styles.childButtonText,
                      selectedChild && selectedChild.id === child.id
                        ? styles.childButtonTextActive
                        : null,
                    ]}
                  >
                    {child.name} - {child.age} yaş
                  </Text>
                </Pressable>
              ))}
            </View>

            <View style={styles.card}>
              <Text style={styles.sectionTitle}>Sorular</Text>

              {questions.map((question, index) => (
                <View key={question.key} style={styles.questionBox}>
                  <Text style={styles.questionText}>
                    {index + 1}. {question.text}
                  </Text>

                  <View style={styles.answerRow}>
                    <Pressable
                      style={[
                        styles.answerButton,
                        answers[question.key] === 0
                          ? styles.answerButtonNoActive
                          : null,
                      ]}
                      onPress={() => setAnswer(question.key, 0)}
                    >
                      <Text style={styles.answerText}>Hayır</Text>
                    </Pressable>

                    <Pressable
                      style={[
                        styles.answerButton,
                        answers[question.key] === 1
                          ? styles.answerButtonYesActive
                          : null,
                      ]}
                      onPress={() => setAnswer(question.key, 1)}
                    >
                      <Text style={styles.answerText}>Evet</Text>
                    </Pressable>
                  </View>
                </View>
              ))}

              <Pressable
                style={styles.saveButton}
                onPress={submitTest}
                disabled={loading}
              >
                <Text style={styles.saveButtonText}>
                  {loading ? "Kaydediliyor..." : "Testi Kaydet"}
                </Text>
              </Pressable>
            </View>

            <View style={styles.card}>
              <Text style={styles.sectionTitle}>Test Geçmişi</Text>

              {testHistory.length === 0 ? (
                <Text style={styles.emptyText}>Henüz test kaydı yok.</Text>
              ) : (
                testHistory.map((item) => (
                  <View key={item.id} style={styles.historyCard}>
                    <Text style={styles.historyTitle}>
                      Risk Düzeyi: {item.risk_level}
                    </Text>
                    <Text style={styles.historyText}>
                      Toplam Puan: {item.total_score}/10
                    </Text>
                    <Text style={styles.historyText}>{item.result_text}</Text>
                    <Text style={styles.historyDate}>
                      Tarih: {item.created_at || "-"}
                    </Text>
                  </View>
                ))
              )}
            </View>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#F3F4F6",
  },
  scrollContent: {
    padding: 20,
    paddingBottom: 40,
  },
  headerCard: {
    backgroundColor: "#FFFFFF",
    padding: 22,
    borderRadius: 20,
    marginBottom: 14,
  },
  card: {
    backgroundColor: "#FFFFFF",
    padding: 18,
    borderRadius: 18,
    marginBottom: 14,
  },
  title: {
    fontSize: 24,
    fontWeight: "900",
    color: "#111827",
    textAlign: "center",
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 14,
    color: "#4B5563",
    textAlign: "center",
    lineHeight: 21,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: "900",
    color: "#111827",
    marginBottom: 12,
  },
  childButton: {
    backgroundColor: "#F3F4F6",
    padding: 13,
    borderRadius: 12,
    marginBottom: 8,
  },
  childButtonActive: {
    backgroundColor: "#2563EB",
  },
  childButtonText: {
    color: "#111827",
    fontWeight: "800",
  },
  childButtonTextActive: {
    color: "#FFFFFF",
  },
  questionBox: {
    backgroundColor: "#F9FAFB",
    padding: 14,
    borderRadius: 14,
    marginBottom: 12,
  },
  questionText: {
    color: "#111827",
    fontSize: 15,
    lineHeight: 21,
    fontWeight: "700",
    marginBottom: 10,
  },
  answerRow: {
    flexDirection: "row",
    gap: 10,
  },
  answerButton: {
    flex: 1,
    backgroundColor: "#E5E7EB",
    padding: 12,
    borderRadius: 10,
    alignItems: "center",
  },
  answerButtonNoActive: {
    backgroundColor: "#059669",
  },
  answerButtonYesActive: {
    backgroundColor: "#DC2626",
  },
  answerText: {
    color: "#FFFFFF",
    fontWeight: "900",
  },
  saveButton: {
    backgroundColor: "#7C3AED",
    padding: 15,
    borderRadius: 13,
    alignItems: "center",
    marginTop: 8,
  },
  saveButtonText: {
    color: "#FFFFFF",
    fontSize: 16,
    fontWeight: "900",
  },
  emptyText: {
    fontSize: 14,
    color: "#6B7280",
    textAlign: "center",
    lineHeight: 21,
  },
  historyCard: {
    backgroundColor: "#EEF2FF",
    padding: 14,
    borderRadius: 14,
    marginBottom: 10,
  },
  historyTitle: {
    fontSize: 16,
    fontWeight: "900",
    color: "#3730A3",
    marginBottom: 6,
  },
  historyText: {
    fontSize: 14,
    color: "#111827",
    lineHeight: 20,
  },
  historyDate: {
    fontSize: 12,
    color: "#6B7280",
    marginTop: 8,
    textAlign: "right",
  },
});