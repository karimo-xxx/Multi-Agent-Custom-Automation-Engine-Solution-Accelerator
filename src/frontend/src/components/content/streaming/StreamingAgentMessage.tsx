import React from "react";
import { AgentMessageData, AgentMessageType, Citation } from "@/models";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypePrism from "rehype-prism";
import { Body1, Button, Tag, makeStyles, tokens, Link } from "@fluentui/react-components";
import { TaskService } from "@/services";
import { Copy } from "@/coral/imports/bundleicons";
import { PersonRegular, GlobeSearch20Regular } from "@fluentui/react-icons";
import { getAgentIcon, getAgentDisplayName } from '@/utils/agentIconUtils';

interface StreamingAgentMessageProps {
  agentMessages: AgentMessageData[];
  planData?: any;
  planApprovalRequest?: any;
}

const useStyles = makeStyles({
  container: {
    maxWidth: '800px',
    margin: '0 auto 32px auto',
    padding: '0 24px',
    display: 'flex',
    alignItems: 'flex-start',
    gap: '16px',
    fontFamily: tokens.fontFamilyBase
  },
  avatar: {
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    flexShrink: 0
  },
  humanAvatar: {
    backgroundColor: 'var(--colorBrandBackground)'
  },
  botAvatar: {
    backgroundColor: 'var(--colorNeutralBackground3)'
  },
  messageContent: {
    flex: 1,
    maxWidth: 'calc(100% - 48px)',
    display: 'flex',
    flexDirection: 'column'
  },
  humanMessageContent: {
    alignItems: 'flex-end'
  },
  botMessageContent: {
    alignItems: 'flex-start'
  },
  agentHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    marginBottom: '8px'
  },
  agentName: {
    fontWeight: '600',
    fontSize: '14px',
    color: 'var(--colorNeutralForeground1)',
    lineHeight: '20px'
  },
  messageBubble: {
    padding: '12px 16px',
    borderRadius: '8px',
    fontSize: '14px',
    lineHeight: '1.5',
    wordWrap: 'break-word'
  },
  humanBubble: {
    backgroundColor: 'var(--colorBrandBackground)',
    color: 'white !important', // Force white text in both light and dark modes
    maxWidth: '80%',
    padding: '12px 16px',
    lineHeight: '1.5',
    alignSelf: 'flex-end'
  },
  botBubble: {
    backgroundColor: 'var(--colorNeutralBackground2)',
    color: 'var(--colorNeutralForeground1)',
    maxWidth: '100%',
    alignSelf: 'flex-start',

  },
 
  clarificationBubble: {
    backgroundColor: 'var(--colorNeutralBackground2)',
    color: 'var(--colorNeutralForeground1)',
    padding: '6px 8px', 
    borderRadius: '8px',
    fontSize: '14px',
    lineHeight: '1.5',
    wordWrap: 'break-word',
    maxWidth: '100%',
    alignSelf: 'flex-start'
  },
  citationsContainer: {
    marginTop: '12px',
    paddingTop: '12px',
    borderTop: '1px solid var(--colorNeutralStroke2)',
    display: 'flex',
    flexDirection: 'column',
    gap: '8px'
  },
  citationItem: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    fontSize: '13px',
    color: 'var(--colorNeutralForeground2)'
  },
  citationIcon: {
    fontSize: '16px',
    color: 'var(--colorBrandForeground1)',
    flexShrink: 0
  },
  citationLink: {
    color: 'var(--colorBrandForeground1)',
    textDecoration: 'none',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    '&:hover': {
      textDecoration: 'underline'
    }
  },

   actionContainer: {
    display: 'flex',
    alignItems: 'center',
    marginTop: '12px',
    paddingTop: '8px',
    borderTop: '1px solid var(--colorNeutralStroke2)'
  },
  
  copyButton: {
    height: '28px',
    width: '28px'
  },
  sampleTag: {
    fontSize: '11px',
    opacity: 0.7
  }
});

// Check if message is a clarification request
const isClarificationMessage = (content: string): boolean => {
  const clarificationKeywords = [
    'need clarification',
    'please clarify',
    'could you provide more details',
    'i need more information',
    'please specify',
    'what do you mean by',
    'clarification about'
  ];
  
  const lowerContent = content.toLowerCase();
  return clarificationKeywords.some(keyword => lowerContent.includes(keyword));
};

const renderAgentMessages = (
  agentMessages: AgentMessageData[], 
  planData?: any, 
  planApprovalRequest?: any
) => {
  const styles = useStyles();
  
  if (!agentMessages?.length) return null;

  // Filter out messages with empty content
  const validMessages = agentMessages.filter(msg => msg.content?.trim());
  if (!validMessages.length) return null;

  return (
    <>
      {validMessages.map((msg, index) => {
        const isHuman = msg.agent_type === AgentMessageType.HUMAN_AGENT;
        const isClarification = !isHuman && isClarificationMessage(msg.content || '');

        return (
          <div
            key={index}
            className={styles.container}
            style={{
              flexDirection: isHuman ? 'row-reverse' : 'row'
            }}
          >
            {/* Avatar */}
            <div className={`${styles.avatar} ${isHuman ? styles.humanAvatar : styles.botAvatar}`}>
              {isHuman ? (
                <PersonRegular style={{ fontSize: '16px', color: 'white' }} />
              ) : (
                getAgentIcon(msg.agent, planData, planApprovalRequest)
              )}
            </div>

            {/* Message Content */}
            <div className={`${styles.messageContent} ${isHuman ? styles.humanMessageContent : styles.botMessageContent}`}>
              {/* Agent Header (only for bots) */}
              {!isHuman && (
                <div className={styles.agentHeader}>
                  <Body1 className={styles.agentName}>
                    {getAgentDisplayName(msg.agent)}
                  </Body1>
                  <Tag
                    appearance="brand"
                  >
                    AI Agent
                  </Tag>
                </div>
              )}

              {/* Message Bubble */}
              <div className={
                isHuman 
                  ? `${styles.messageBubble} ${styles.humanBubble}`
                  : isClarification 
                    ? styles.clarificationBubble 
                    : `${styles.messageBubble} ${styles.botBubble}`
              }>
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  rehypePlugins={[rehypePrism]}
                  components={{
                      a: ({ node, ...props }) => (
                        <a
                          {...props}
                          style={{
                            color: 'var(--colorNeutralBrandForeground1)',
                            textDecoration: 'none'
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.textDecoration = 'underline';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.textDecoration = 'none';
                          }}
                        />
                      )
                    }}
                >
                  {TaskService.cleanHRAgent(msg.content) || ""}
                </ReactMarkdown>
              </div>

              {/* Citations Section */}
              {msg.citations && msg.citations.length > 0 && (
                <div className={styles.citationsContainer}>
                  {msg.citations.map((citation, citIndex) => (
                    <div key={citIndex} className={styles.citationItem}>
                      <GlobeSearch20Regular className={styles.citationIcon} />
                      <Link
                        href={citation.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.citationLink}
                      >
                        {citation.title || citation.url}
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </>
  );
};

export default renderAgentMessages;