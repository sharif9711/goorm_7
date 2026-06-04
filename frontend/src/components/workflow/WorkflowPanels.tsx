import { CheckOutlined, CloseOutlined } from '@ant-design/icons';
import { Alert, Button, Card, Input, Space, Tag, Typography } from 'antd';
import { useState } from 'react';
import { analysisApi } from '@/api';
import type { AnalysisResult } from '@/types';

const { Text, Paragraph } = Typography;

interface HumanReviewPanelProps {
  result: AnalysisResult;
  onResumed: (result: AnalysisResult) => void;
}

export default function HumanReviewPanel({ result, onResumed }: HumanReviewPanelProps) {
  const [feedback, setFeedback] = useState('');
  const [loading, setLoading] = useState(false);

  const handleReview = async (approved: boolean) => {
    setLoading(true);
    try {
      await analysisApi.resume(result.task_id, { approved, feedback: feedback || undefined });
      const { data } = await analysisApi.getResult(result.task_id);
      onResumed(data);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title="Human-in-the-Loop 검토"
      style={{ marginBottom: 24, borderColor: '#faad14' }}
      extra={<Tag color="gold">검토 필요</Tag>}
    >
      <Alert
        type="warning"
        showIcon
        message="AI 분석 결과를 검토해주세요"
        description={`품질 점수: ${result.quality_score.toFixed(0)} — 승인 시 리포트가 생성됩니다.`}
        style={{ marginBottom: 16 }}
      />

      {result.insights.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Text strong>인사이트 미리보기</Text>
          <ul style={{ marginTop: 8 }}>
            {result.insights.slice(0, 5).map((item, i) => (
              <li key={i}><Text>{item}</Text></li>
            ))}
          </ul>
        </div>
      )}

      <Input.TextArea
        rows={3}
        placeholder="수정 피드백 (선택)"
        value={feedback}
        onChange={(e) => setFeedback(e.target.value)}
        style={{ marginBottom: 16 }}
      />

      <Space>
        <Button
          type="primary"
          icon={<CheckOutlined />}
          loading={loading}
          onClick={() => handleReview(true)}
        >
          승인 및 리포트 생성
        </Button>
        <Button
          danger
          icon={<CloseOutlined />}
          loading={loading}
          onClick={() => handleReview(false)}
        >
          거부
        </Button>
      </Space>
    </Card>
  );
}

interface WorkflowProgressProps {
  stepsCompleted: string[];
  currentStep?: string;
}

export function WorkflowProgress({ stepsCompleted, currentStep }: WorkflowProgressProps) {
  const allSteps = [
    'planner', 'trend_collector', 'analysis', 'insight_generator',
    'critic', 'human_review', 'report', 'evaluation',
  ];

  return (
    <Card title="Workflow Graph" size="small" style={{ marginBottom: 16 }}>
      <Space wrap>
        {allSteps.map((step) => {
          const done = stepsCompleted.some((s) => s.startsWith(step) || s === step);
          const active = currentStep === step;
          return (
            <Tag key={step} color={done ? 'green' : active ? 'blue' : 'default'}>
              {step}
            </Tag>
          );
        })}
      </Space>
    </Card>
  );
}

interface EvaluationPanelProps {
  evaluation?: AnalysisResult['evaluation'];
}

export function EvaluationPanel({ evaluation }: EvaluationPanelProps) {
  if (!evaluation) return null;

  return (
    <Card title="Agent Evaluation" size="small" style={{ marginBottom: 16 }}>
      <Paragraph>
        Overall Score: <Text strong>{evaluation.overall_score}</Text>
        {' '}
        <Tag color={evaluation.passed ? 'green' : 'orange'}>
          {evaluation.passed ? 'PASSED' : 'NEEDS IMPROVEMENT'}
        </Tag>
      </Paragraph>
      {evaluation.recommendations?.map((rec, i) => (
        <Paragraph key={i} type="secondary">• {rec}</Paragraph>
      ))}
    </Card>
  );
}
