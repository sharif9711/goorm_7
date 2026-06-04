import { SearchOutlined } from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';
import { Button, Card, Col, Input, List, Progress, Row, Select, Spin, Tag, Typography } from 'antd';
import { useState } from 'react';
import { analysisApi } from '@/api';
import HumanReviewPanel, { EvaluationPanel, WorkflowProgress } from '@/components/workflow/WorkflowPanels';
import { useAnalysisStore } from '@/stores/authStore';
import type { AnalysisResult } from '@/types';

const { Title, Text, Paragraph } = Typography;

const ANALYSIS_TYPES = [
  { value: 'keyword_search', label: '키워드 검색' },
  { value: 'trending', label: '급상승 영상' },
  { value: 'full', label: '전체 분석' },
  { value: 'content_ideas', label: '콘텐츠 아이디어' },
];

const PERIODS = [
  { value: '24h', label: '24시간' },
  { value: '7d', label: '7일' },
  { value: '30d', label: '30일' },
];

export default function TrendExplorerPage() {
  const [query, setQuery] = useState('');
  const [analysisType, setAnalysisType] = useState('keyword_search');
  const [period, setPeriod] = useState('7d');
  const setResult = useAnalysisStore((s) => s.setResult);
  const currentResult = useAnalysisStore((s) => s.currentResult);

  const mutation = useMutation({
    mutationFn: (data: { query: string; analysis_type: string; period: string }) =>
      analysisApi.analyze(data).then(async (res) => {
        const result = await analysisApi.getResult(res.data.task_id);
        return result.data;
      }),
    onSuccess: (data: AnalysisResult) => setResult(data),
  });

  const handleSearch = () => {
    if (!query.trim()) return;
    mutation.mutate({ query, analysis_type: analysisType, period });
  };

  const result = currentResult || mutation.data;

  return (
    <div>
      <Title level={2}>Trend Explorer</Title>
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[12, 12]} align="middle">
          <Col xs={24} md={10}>
            <Input
              size="large"
              placeholder="키워드 입력 (예: AI Automation)"
              prefix={<SearchOutlined />}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onPressEnter={handleSearch}
            />
          </Col>
          <Col xs={12} md={5}>
            <Select size="large" style={{ width: '100%' }} value={analysisType} onChange={setAnalysisType} options={ANALYSIS_TYPES} />
          </Col>
          <Col xs={12} md={4}>
            <Select size="large" style={{ width: '100%' }} value={period} onChange={setPeriod} options={PERIODS} />
          </Col>
          <Col xs={24} md={5}>
            <Button type="primary" size="large" block icon={<SearchOutlined />} loading={mutation.isPending} onClick={handleSearch}>
              분석 시작
            </Button>
          </Col>
        </Row>
      </Card>

      {mutation.isPending && (
        <Card style={{ textAlign: 'center', padding: 48 }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 16 }}>LangGraph 워크플로우가 YouTube 데이터를 분석 중입니다...</Paragraph>
        </Card>
      )}

      {result && !mutation.isPending && (
        <>
          {result.status === 'awaiting_human' && (
            <HumanReviewPanel result={result} onResumed={(data) => setResult(data)} />
          )}

          <WorkflowProgress
            stepsCompleted={result.steps_completed || []}
          />

          <EvaluationPanel evaluation={result.evaluation} />

          <Row gutter={[16, 16]}>
          <Col xs={24} lg={8}>
            <Card title="분석 계획">
              <List size="small" dataSource={result.plan} renderItem={(item) => <List.Item>{item}</List.Item>} />
              <Progress percent={result.quality_score} status="active" style={{ marginTop: 16 }} />
              <Text type="secondary">품질 점수: {result.quality_score.toFixed(0)}</Text>
            </Card>
          </Col>
          <Col xs={24} lg={16}>
            <Card title="인사이트">
              <List
                dataSource={result.insights}
                renderItem={(item) => <List.Item><Tag color="blue">Insight</Tag>{item}</List.Item>}
              />
            </Card>
          </Col>
          {(result.data as { keywords?: Array<{ keyword: string; trend_score: number }> }).keywords && (
            <Col xs={24}>
              <Card title="키워드 분석">
                <List
                  grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 4 }}
                  dataSource={(result.data as { keywords: Array<{ keyword: string; trend_score: number; frequency: number }> }).keywords}
                  renderItem={(item) => (
                    <List.Item>
                      <Card size="small">
                        <Tag color="geekblue">{item.keyword}</Tag>
                        <div>트렌드 점수: {item.trend_score.toFixed(1)}</div>
                      </Card>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          )}
          {result.content_ideas && Object.keys(result.content_ideas).length > 0 && (
            <Col xs={24}>
              <Card title="콘텐츠 아이디어">
                {Object.entries(result.content_ideas).map(([category, ideas]) => (
                  <div key={category} style={{ marginBottom: 16 }}>
                    <Title level={5}>{category === 'shorts' ? '쇼츠' : category === 'longform' ? '롱폼' : '블로그'}</Title>
                    <List size="small" dataSource={ideas.slice(0, 10)} renderItem={(item) => <List.Item>{item}</List.Item>} />
                  </div>
                ))}
              </Card>
            </Col>
          )}
          {result.tool_calls && result.tool_calls.length > 0 && (
            <Col xs={24}>
              <Card title="Tool Calls (OpenAI Agents SDK)">
                <List
                  size="small"
                  dataSource={result.tool_calls}
                  renderItem={(item) => (
                    <List.Item>
                      <Tag color="purple">{item.tool}</Tag>
                      <Text type="secondary">{JSON.stringify(item.arguments)}</Text>
                    </List.Item>
                  )}
                />
              </Card>
            </Col>
          )}
        </Row>
        </>
      )}
    </div>
  );
}
