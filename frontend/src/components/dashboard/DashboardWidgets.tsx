import { Card, Col, List, Row, Skeleton, Tag, Typography } from 'antd';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';

const { Title, Text } = Typography;

interface StatCardProps {
  title: string;
  value: string | number;
  color?: string;
  loading?: boolean;
}

export function StatCard({ title, value, color = '#1677ff', loading }: StatCardProps) {
  return (
    <motion.div whileHover={{ scale: 1.02 }} transition={{ type: 'spring', stiffness: 300 }}>
      <Card loading={loading} style={{ borderTop: `3px solid ${color}` }}>
        <Text type="secondary">{title}</Text>
        <Title level={3} style={{ margin: '8px 0 0' }}>{value}</Title>
      </Card>
    </motion.div>
  );
}

interface KeywordWidgetProps {
  keywords: Array<{ keyword: string; trend_score: number; frequency: number }>;
  loading?: boolean;
}

export function KeywordWidget({ keywords, loading }: KeywordWidgetProps) {
  return (
    <Card title="오늘의 키워드" loading={loading}>
      <List
        dataSource={keywords}
        renderItem={(item) => (
          <List.Item>
            <Tag color="blue">{item.keyword}</Tag>
            <Text type="secondary">점수 {item.trend_score.toFixed(1)}</Text>
          </List.Item>
        )}
      />
    </Card>
  );
}

interface ChannelWidgetProps {
  channels: Array<{ title: string; growth_score: number; subscribers: number }>;
  loading?: boolean;
}

export function RisingChannelsWidget({ channels, loading }: ChannelWidgetProps) {
  return (
    <Card title="급상승 채널" loading={loading}>
      <List
        dataSource={channels}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta title={item.title} description={`구독자 ${item.subscribers.toLocaleString()}`} />
            <Tag color="green">{item.growth_score.toFixed(1)}</Tag>
          </List.Item>
        )}
      />
    </Card>
  );
}

interface VideoWidgetProps {
  videos: Array<{ title: string; views: number; trend_score: number }>;
  loading?: boolean;
}

export function RisingVideosWidget({ videos, loading }: VideoWidgetProps) {
  return (
    <Card title="급상승 영상" loading={loading}>
      <List
        dataSource={videos}
        renderItem={(item) => (
          <List.Item>
            <List.Item.Meta title={item.title.slice(0, 60)} description={`조회수 ${item.views.toLocaleString()}`} />
          </List.Item>
        )}
      />
    </Card>
  );
}

interface RecentAnalysisProps {
  analyses: Array<{ id: number; title: string; created_at: string }>;
  loading?: boolean;
}

export function RecentAnalysisWidget({ analyses, loading }: RecentAnalysisProps) {
  return (
    <Card title="최근 분석" loading={loading}>
      <List
        dataSource={analyses}
        renderItem={(item) => (
          <List.Item>
            <Link to={`/reports/${item.id}`}>{item.title}</Link>
            <Text type="secondary">{new Date(item.created_at).toLocaleDateString('ko-KR')}</Text>
          </List.Item>
        )}
      />
    </Card>
  );
}

interface RecommendationsProps {
  recommendations: string[];
  loading?: boolean;
}

export function ContentRecommendationsWidget({ recommendations, loading }: RecommendationsProps) {
  return (
    <Card title="콘텐츠 추천" loading={loading}>
      <List
        dataSource={recommendations}
        renderItem={(item, i) => (
          <List.Item>
            <Tag color="purple">{i + 1}</Tag> {item}
          </List.Item>
        )}
      />
    </Card>
  );
}

export function DashboardSkeleton() {
  return (
    <Row gutter={[16, 16]}>
      {[1, 2, 3, 4].map((i) => (
        <Col xs={24} sm={12} lg={6} key={i}>
          <Card><Skeleton active /></Card>
        </Col>
      ))}
    </Row>
  );
}
