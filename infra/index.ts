import * as cdk from 'aws-cdk-lib';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as ecs from 'aws-cdk-lib/aws-ecs';
import * as efs from 'aws-cdk-lib/aws-efs';
import * as elb from 'aws-cdk-lib/aws-elasticloadbalancingv2';
import * as logs from 'aws-cdk-lib/aws-logs';
import { Construct } from 'constructs';

class QuipSharePointStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // VPC
    const vpc = new ec2.Vpc(this, 'Vpc', {
      maxAzs: 2,
      natGateways: 1,
    });

    // EFS for SQLite + file storage persistence
    const fileSystem = new efs.FileSystem(this, 'AppData', {
      vpc,
      removalPolicy: cdk.RemovalPolicy.RETAIN,
      performanceMode: efs.PerformanceMode.GENERAL_PURPOSE,
      encrypted: true,
    });

    const accessPoint = fileSystem.addAccessPoint('AppAccessPoint', {
      path: '/appdata',
      createAcl: { ownerGid: '1000', ownerUid: '1000', permissions: '755' },
      posixUser: { gid: '1000', uid: '1000' },
    });

    // ECS Cluster
    const cluster = new ecs.Cluster(this, 'Cluster', { vpc });

    // Task Definition
    const taskDef = new ecs.FargateTaskDefinition(this, 'TaskDef', {
      memoryLimitMiB: 1024,
      cpu: 512,
      runtimePlatform: {
        cpuArchitecture: ecs.CpuArchitecture.ARM64,
        operatingSystemFamily: ecs.OperatingSystemFamily.LINUX,
      },
    });

    // Mount EFS volume
    taskDef.addVolume({
      name: 'appdata',
      efsVolumeConfiguration: {
        fileSystemId: fileSystem.fileSystemId,
        transitEncryption: 'ENABLED',
        authorizationConfig: { accessPointId: accessPoint.accessPointId, iam: 'ENABLED' },
      },
    });

    // Container
    const container = taskDef.addContainer('App', {
      image: ecs.ContainerImage.fromAsset('..', {
        file: 'Dockerfile',
        platform: cdk.aws_ecr_assets.Platform.LINUX_ARM64,
      }),
      logging: ecs.LogDrivers.awsLogs({
        streamPrefix: 'quip-sharepoint',
        logRetention: logs.RetentionDays.TWO_WEEKS,
      }),
      environment: {
        JWT_SECRET: 'change-me-in-production',
      },
      portMappings: [{ containerPort: 8000 }],
      healthCheck: {
        command: ['CMD-SHELL', 'curl -f http://localhost:8000/health || exit 1'],
        interval: cdk.Duration.seconds(30),
        timeout: cdk.Duration.seconds(5),
        retries: 3,
      },
    });

    container.addMountPoints({
      sourceVolume: 'appdata',
      containerPath: '/app/data',
      readOnly: false,
    });

    // ALB
    const alb = new elb.ApplicationLoadBalancer(this, 'ALB', {
      vpc,
      internetFacing: true,
    });

    // Fargate Service
    const service = new ecs.FargateService(this, 'Service', {
      cluster,
      taskDefinition: taskDef,
      desiredCount: 1,
      assignPublicIp: false,
      platformVersion: ecs.FargatePlatformVersion.LATEST,
    });

    // Allow EFS access
    fileSystem.connections.allowDefaultPortFrom(service);
    fileSystem.grantRootAccess(taskDef.taskRole);

    // ALB Target Group with stickiness for WebSocket
    const targetGroup = new elb.ApplicationTargetGroup(this, 'TG', {
      vpc,
      port: 8000,
      protocol: elb.ApplicationProtocol.HTTP,
      targets: [service],
      healthCheck: {
        path: '/health',
        interval: cdk.Duration.seconds(30),
        healthyThresholdCount: 2,
      },
      stickinessCookieDuration: cdk.Duration.hours(1),
    });

    // HTTP Listener
    alb.addListener('HttpListener', {
      port: 80,
      defaultTargetGroups: [targetGroup],
    });

    // Allow ALB -> ECS
    service.connections.allowFrom(alb, ec2.Port.tcp(8000));

    // Outputs
    new cdk.CfnOutput(this, 'URL', {
      value: `http://${alb.loadBalancerDnsName}`,
      description: 'Application URL',
    });
  }
}

const app = new cdk.App();
new QuipSharePointStack(app, 'QuipSharePointStack', {
  env: {
    account: '444201840874',
    region: 'ap-northeast-1',
  },
});
