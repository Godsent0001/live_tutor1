// lib/config/api_config.dart

class ApiConfig {
  static const String baseUrl = 'http://10.53.210.63:8000';

  // Users
  static const String register = '/users/create';  // only endpoint that exists
  static String getUser(String userId) => '/users/$userId';

  // Lessons
  static const String createLesson = '/lessons/create';
  static String getLesson(String lessonId) => '/lessons/$lessonId';

  // Sessions
  static const String startSession = '/sessions/start';
  static String getSession(String sessionId) => '/sessions/$sessionId';
  static String currentStep(String sessionId) =>
      '/sessions/$sessionId/current-step';
  static String nextStep(String sessionId) => '/sessions/$sessionId/next-step';
  static String pauseSession(String sessionId) =>
      '/sessions/$sessionId/pause';
  static String resumeSession(String sessionId) =>
      '/sessions/$sessionId/resume';

  // Responses
  static const String submitResponse = '/responses/submit';


  // Module Q&A
  static const String askModuleQuestion = '/modules/ask';
}
