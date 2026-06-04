import { useMutation, useQuery } from '@tanstack/react-query';
import { Button, Card, Col, Input, List, Row, Table, Tag, Typography } from 'antd';
import { useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { analysisApi, channelsApi } from '@/api';

const { Title } = Typography;

export default function ChannelAnalyzerPage() {
  const [channelUrl, setChannelUrl] = useState('');
  const [competitorUrl, setCompetitorUrl] = useState('');

  const { data: channels, isLoading } = useQuery({
    queryKey: ['channels'],
    queryFn: () => channelsApi.list({ limit: 20, sort_by: 'growth_score' }).then((r) => r.data),
  });

  const mutation = useMutation({
    mutationFn: () =>
      analysisApi.analyze({
        query: 'channel analysis',
        analysis_type: 'competitor',
        channel_url: channelUrl,
        competitor_urls: competitorUrl ? [competitorUrl] : [],
      }).then(async (res) => {
        const result = await analysisApi.getResult(res.data.task_id);
        return result.data;
      }),
  });

  const gapData = (mutation.data?.data as { gap_analysis?: { opportunities: string[]; user_metrics: { subscribers: number; views: number }; competitor_avg: { subscribers: number; views: number } } })?.gap_analysis;

  const chartData = gapData ? [
    { name: '구독자', user: gapData.user_metrics.subscribers, competitor: gapData.competitor_avg.subscribers },
    { name: '조회수', user: gapData.user_metrics.views, competitor: gapData.competitor_avg.views },
  ] : [];

  const columns = [
    { title: '채널', dataIndex: 'title', key: 'title' },
    { title: '구독자', dataIndex: 'subscriber_count', key: 'subscribers', render: (v: number) => v.toLocaleString() },
    { title: '영상 수', dataIndex: 'video_count', key: 'videos' },
    { title: 'Growth Score', dataIndex: 'growth_score', key: 'growth', render: (v: number) => <Tag color="green">{v.toFixed(1)}</Tag> },
  ];

  return (
    <div>
      <Title level={2}>Channel Analyzer</Title>
      <Card style={{ marginBottom: 24 }}>
        <Row gutter={[12, 12]}>
          <Col xs={24} md={10}>
            <Input placeholder="내 채널 URL" value={channelUrl} onChange={(e) => setChannelUrl(e.target.value)} size="large" />
          </Col>
          <Col xs={24} md={10}>
            <Input placeholder="경쟁 채널 URL (선택)" value={competitorUrl} onChange={(e) => setCompetitorUrl(e.target.value)} size="large" />
          </Col>
          <Col xs={24} md={4}>
            <Button type="primary" size="large" block loading={mutation.isPending} onClick={() => mutation.mutate()} disabled={!channelUrl}>
              분석
            </Button>
          </Col>
        </Row>
      </Card>

      {gapData && (
        <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
          <Col xs={24} lg={12}>
            <Card title="Gap Analysis">
              <List dataSource={gapData.opportunities} renderItem={(item) => <List.Item><Tag color="orange">기회</Tag>{item}</List.Item>} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="비교 차트">
              <ResponsiveContainer width="100%" height={250}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="user" fill="#1677ff" name="내 채널" />
                  <Bar dataKey="competitor" fill="#52c41a" name="경쟁 평균" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>
      )}

      <Card title="성장 채널 목록">
        <Table dataSource={channels} columns={columns} rowKey="id" loading={isLoading} pagination={{ pageSize: 10 }} />
      </Card>
    </div>
  );
}
