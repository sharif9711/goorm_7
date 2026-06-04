import { useQuery } from '@tanstack/react-query';
import { Col, Row, Typography } from 'antd';
import { trendsApi } from '@/api';
import {
  ContentRecommendationsWidget,
  DashboardSkeleton,
  KeywordWidget,
  RecentAnalysisWidget,
  RisingChannelsWidget,
  RisingVideosWidget,
  StatCard,
} from '@/components/dashboard/DashboardWidgets';

const { Title } = Typography;

export default function DashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['trends-overview'],
    queryFn: () => trendsApi.getOverview().then((r) => r.data),
  });

  if (isLoading) return <DashboardSkeleton />;

  const overview = data || {
    top_keywords: [],
    rising_channels: [],
    rising_videos: [],
    recent_analyses: [],
    content_recommendations: [],
  };

  return (
    <div>
      <Title level={2}>Dashboard</Title>
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="트렌딩 키워드" value={overview.top_keywords.length} color="#1677ff" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="성장 채널" value={overview.rising_channels.length} color="#52c41a" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="급상승 영상" value={overview.rising_videos.length} color="#faad14" />
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <StatCard title="최근 분석" value={overview.recent_analyses.length} color="#eb2f96" />
        </Col>
      </Row>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <KeywordWidget keywords={overview.top_keywords} />
        </Col>
        <Col xs={24} lg={12}>
          <RisingChannelsWidget channels={overview.rising_channels} />
        </Col>
        <Col xs={24} lg={12}>
          <RisingVideosWidget videos={overview.rising_videos} />
        </Col>
        <Col xs={24} lg={12}>
          <RecentAnalysisWidget analyses={overview.recent_analyses} />
        </Col>
        <Col xs={24}>
          <ContentRecommendationsWidget recommendations={overview.content_recommendations} />
        </Col>
      </Row>
    </div>
  );
}
