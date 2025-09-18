import React from 'react';
import { Card } from 'react-bootstrap';

const StatisticCard = ({ title, value, icon, color }) => {
    return (
        <Card className={`mb-3 shadow-sm`}>
            <Card.Body>
                <div className="d-flex align-items-center">
                    <div className={`me-3 text-${color}`}>
                        {icon}
                    </div>
                    <div>
                        <h6 className="mb-1 text-muted">{title}</h6>
                        <h4 className="mb-0">{value}</h4>
                    </div>
                </div>
            </Card.Body>
        </Card>
    );
};

export default StatisticCard;
