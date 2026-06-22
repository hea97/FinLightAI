const kakaoAlertItems = [
  '시장 급변 알림',
  '관심 산업 뉴스 알림',
  '포트폴리오 위험 신호 알림',
  'AI 브리핑 요약 알림',
];

export function KakaoAlertGuide() {
  return (
    <section className="kakao-alert-guide">
      <h2>카카오 알림으로 받을 수 있는 내용</h2>
      <p>
        FinLightAI는 사용자가 놓치기 쉬운 시장 변화와 관심 산업 이슈를
        카카오 알림으로 전달할 수 있습니다.
      </p>

      <ul>
        {kakaoAlertItems.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}
