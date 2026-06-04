import { useQuery } from '@tanstack/react-query';
import { Card, Col, Input, List, Row, Tag, Typography } from 'antd';
import { useMemo, useState } from 'react';
import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { keywordsApi } from '@/api';

const { Title } = Typography;

export default function KeywordExplorerPage() {
  const [search, setSearch] = useState('');

  const { data: keywords, isLoading } = useQuery({
    queryKey: ['keywords'],
    queryFn: () => keywordsApi.list({ limit: 50 }).then((r) => r.data),
  });

  const filtered = useMemo(() => {
    if (!keywords) return [];
    if (!search) return keywords;
    return keywords.filter((k) => k.keyword.toLowerCase().includes(search.toLowerCase()));
  }, [keywords, search]);

  const chartData = filtered.slice(0, 10).map((k, i) => ({
    name: k.keyword.slice(0, 12),
    trend: k.trend_score,
    growth: k.growth_rate * 10,
    index: i,
  }));

  return (
    <div>
      <Title level={2}>Keyword Explorer</Title>
      <Card style={{ marginBottom: 24 }}>
        <Input.Search
          placeholder="키워드 검색"
          size="large"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          loading={isLoading}
        />
      </Card>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={14}>
          <Card title="키워드 목록" loading={isLoading}>
            <List
              dataSource={filtered}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={<Tag color="blue">{item.keyword}</Tag>}
                    description={`빈도 ${item.frequency} · 경쟁도 ${item.competition_score.toFixed(1)}`}
                  />
                  <div>
                    <Tag color="green">트렌드 {item.trend_score.toFixed(1)}</Tag>
                    <Tag color="orange">성장 {item.growth_rate.toFixed(1)}x</Tag>
                  </div>
                </List.Item>
              )}
            />
          </Card>
        </Col>
        <Col xs={24} lg={10}>
          <Card title="성장 그래프">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="trend" stroke="#1677ff" name="트렌드 점수" />
                <Line type="monotone" dataKey="growth" stroke="#52c41a" name="성장률" />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  );
}
